import re

from django.shortcuts import redirect
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import (HttpResponseRedirect, HttpResponse,
                         HttpResponseForbidden, HttpResponseServerError)
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone

from dropbox import DropboxOAuth2Flow, oauth, dropbox
from dropbox.files import FileMetadata, FolderMetadata
from dropbox.client import DropboxClient

from generic import custom_funcs

from .models import Dropbox


# --------------------- AUTHORIZATION VIEWS ---------------------------
def get_dropbox_auth_flow(web_app_session):
    redirect_uri = '{}dropbox/auth_finish/'.format(settings.SITE_PATH)
    return DropboxOAuth2Flow(
        settings.DROPBOX_APP_KEY, settings.DROPBOX_APP_SECRET,
        redirect_uri, web_app_session, "dropbox-auth-csrf-token")


# URL handler for /dropbox-auth-start
def dropbox_auth_start(request):
    authorize_url = get_dropbox_auth_flow(request.session).start()
    return HttpResponseRedirect(authorize_url)


# URL handler for /dropbox-auth-finish
def dropbox_auth_finish(request):
    try:
        access_token, user_id, url_state = \
            get_dropbox_auth_flow(request.session).finish(request.GET)
    except oauth.BadRequestException, e:
        return HttpResponse(status=400)
    except oauth.BadStateException, e:
        # Start the auth flow again.
        return HttpResponseRedirect(
            '{}dropbox/auth_start/'.format(settings.SITE_PATH))
    except oauth.CsrfException, e:
        return HttpResponseForbidden()
    except oauth.NotApprovedException, e:
        return HttpResponseRedirect(reverse('auth:logout'))
    except oauth.ProviderException, e:
        raise e

    if access_token:
        user = request.user
        user.is_active = True
        user.save()
        dropbox_profile = Dropbox.objects.get_or_create(user=user)[0]
        dropbox_profile.access_token = access_token
        dropbox_profile.save()
    return redirect(reverse('notes:main'))
# ------------------------------------------------------------------


# --------------------- GET API VIEWS ---------------------------
def dropbox_get_connection(user, type_connection='dbx'):
    access_token = dropbox_get_access_token(user)

    if type_connection == 'dbx':
        return dropbox.Dropbox(access_token)
    elif type_connection == 'client':
        return DropboxClient(access_token)


def dropbox_get_access_token(user):
    try:
        access_token = \
            User.objects.get(pk=user.pk).dropbox.access_token
    except:
        pass # doing something if hasn't access token

    return access_token
# -----------------------------------------------------------


# --------------------- GET NOTES ---------------------------
def dropbox_get_notes_version_search(request):
    # TEST TEST TEST
    admin = User.objects.get(pk=1)

    dbx = dropbox_get_connection(admin)
    client = dropbox_get_connection(admin, 'client')

    result = get_notes_by_search(dbx)
    result = custom_funcs.sorted_by_time(result)

    res = {}
    for file in result:
        res = custom_funcs.format_date(file, res)

    order_res = custom_funcs.format_get_dict_full_info(result, client)

    return JsonResponse({'format_result': res, 'result': order_res})


def dropbox_get_notes_version_alt(request):
    # TEST TEST TEST
    admin = User.objects.get(pk=1)
    dbx = dropbox_get_connection(admin)

    days = get_notes_by_exceptions(dbx)
    res_list = custom_funcs.sorted_by_time(days)
    res_dict = {}
    for file in res_list:
        res_dict = custom_funcs.format_date(file, res_dict)

    return JsonResponse({'format_result': res_dict, 'result': res_list})


def get_notes_by_exceptions(dbx):
    result = []
    REGEXP_FOR_MONTH_FOLDERS = '{}'.format('|'.join(settings.FOLDER_NAME_MONTH))

    dirty_years_folders = dbx.files_list_folder('').entries
    for clean_years_folder in dirty_years_folders:
        if isinstance(clean_years_folder, FolderMetadata):
            if re.match('(?:19|20)\d\d',
                clean_years_folder.name):

                dirty_month_folders = \
                    dbx.files_list_folder(clean_years_folder.path_lower).entries
                for clean_month_folder in dirty_month_folders:
                    if isinstance(clean_month_folder, FolderMetadata):
                        if re.match(REGEXP_FOR_MONTH_FOLDERS,
                            clean_month_folder.name, re.IGNORECASE):

                            dirty_days_folders = \
                                dbx.files_list_folder(clean_month_folder.path_lower).entries
                            for clean_days_folder in dirty_days_folders:
                                if isinstance(clean_days_folder, FolderMetadata):
                                    if re.match('\d\d',
                                        clean_days_folder.name):

                                        dirty_files = \
                                            dbx.files_list_folder(clean_days_folder.path_lower).entries
                                        for clean_file in dirty_files:
                                            if isinstance(clean_file, FileMetadata):
                                                if re.match('deez_(.*)\.txt$',
                                                    clean_file.name):

                                                    result.append(clean_file.path_lower)
    return result


def get_notes_by_search(dbx):
    matches = dbx.files_search('', 'deez_').matches
    result = []
    regex = settings.REGEX_FILES

    for search_match in matches:
        if isinstance(search_match.metadata, FileMetadata):
            if re.match(regex, search_match.metadata.path_lower):
                result.append(search_match.metadata.path_lower)

    return result


# def dropbox_get_notes(request):
#     # TEST TEST TEST
#     admin = User.objects.get(pk=1)

#     dbx = dropbox_get_connection(admin)

#     all_files = dbx.files_list_folder('', recursive=True).entries
#     files = []
#     pattern = settings.REGEX_FILES
#     for dirty_file in all_files:
#         if isinstance(dirty_file, FileMetadata):
#             if re.match(pattern, dirty_file.path_lower):
#                 files.append(dirty_file.path_lower)

#     return JsonResponse({'paths': files, 'length': len(all_files)})

# -----------------------------------------------------------


# --------------------- Create/Edit NOTE ---------------------------
def dropbox_create_or_edit_note(request):
    # TEST TEST TEST
    admin = User.objects.get(pk=1)
    client = dropbox_get_connection(admin, 'client')
    new_text = request.GET.get('new_text', 'something_new')
    note_path = request.GET.get('path')

    action = request.GET.get('action', 'edit')
    overwrite = bool(action == 'edit')

    if action == 'create':
        project = request.GET.get('project', settings.DROPBOX_DEFAULT_PROJECT)
        tag = request.GET.get('tag', settings.DROPBOX_DEFAULT_TAG)
        note_path = \
            timezone.now().strftime('/%Y/%b/%d/deez_{}_{}_%I:%M%p.txt').format(project, tag)


    if new_text:
        client.put_file(note_path, new_text, overwrite=overwrite)
        return JsonResponse({'res': 'success'})


def dropbox_change_meta_note(request):
    # TEST TEST TEST
    admin = User.objects.get(pk=1)
    client = dropbox_get_connection(admin, 'client')

    path = request.GET.get('path')
    project = request.GET.get('project')
    tag = request.GET.get('tag')
    path_list = path.split('/')
    if client.search('/{}/'.format('/'.join(path_list[1:-1])), path_list[-1]):
        note_name = path.split('_')
        if project:
            note_name[1] = project
        if tag:
            note_name[2] = tag

        client.file_move(path, '_'.join(note_name))
        return JsonResponse({'res': 'success'})
    else:
        return JsonResponse({'res': 'file not find'})
# -----------------------------------------------------------


# --------------------- Search Note/Folder ------------------
def dropbox_search(request):
    # TEST TEST TEST
    admin = User.objects.get(pk=1)
    dbx = dropbox_get_connection(admin)

    query = request.GET.get('query')
    result = []
    matches = dbx.files_search('', query).matches

    for search_match in matches:
        result.append(search_match.metadata.path_lower)
    return JsonResponse({'result': result})
# -----------------------------------------------------------


# --------------------- META DATA VIEWS ---------------------
def dropbox_get_meta_files(request):
    # # # TEST TEST TEST
    # admin = User.objects.get(pk=1)
    # client = dropbox_get_connection(admin, 'client')

    client = dropbox_get_connection(request.user, 'client')
    search_type = request.GET.get('search_type')
    if search_type:
        res = dropbox_get_meta_data(search_type, client)
        if search_type == 'projects':
            default_name = settings.DROPBOX_DEFAULT_PROJECT
        else:
            default_name = settings.DROPBOX_DEFAULT_TAG
        res = [default_name] + res

        return JsonResponse({'result': res})
    else:
        return JsonResponse({'errors': 'not valible query'})


def dropbox_get_meta_data(type_meta_data, api):
    if type_meta_data == 'projects':
        file_name = settings.DROPBOX_PROJECTS_FILE
    elif type_meta_data == 'tags':
        file_name = settings.DROPBOX_TAGS_FILE

    if api.search(settings.DROPBOX_META_PATH, file_name):
        file = api.get_file(settings.DROPBOX_META_PATH + file_name)
        return filter(None, file.read().split('\n'))
    else:
        return []


def dropbox_add_or_del_meta_files(request):
    # TEST TEST TEST
    admin = User.objects.get(pk=1)
    client = dropbox_get_connection(admin, 'client')

    search_type = request.GET.get('search_type', '')
    query_name = request.GET.get('query_name', '')
    action = request.GET.get('action', '')

    if search_type == 'projects':
        file_name = settings.DROPBOX_PROJECTS_FILE
    elif search_type == 'tags':
        file_name = settings.DROPBOX_TAGS_FILE

    if query_name:
        res = dropbox_get_meta_data(search_type, client)
        if action == 'add':
            if query_name not in res:
                res.append(query_name)
            else:
                return HttpResponseServerError(
                    'Dublicate {} name'.format(search_type[:-1]))
        elif action == 'delete':
            if query_name in res:
                res.remove(query_name)
            else:
                return HttpResponseServerError(
                    'Not find {}'.format(search_type[:-1]))
        client.put_file(settings.DROPBOX_META_PATH + file_name, '\n'.join(res),
                        overwrite=True)
        return JsonResponse({'res': 'Successfully added'})
    else:
        return HttpResponseServerError('Bad request')
# -----------------------------------------------------------


# def dropbox_create_note(request):
#     # TEST TEST TEST
#     admin = User.objects.get(pk=1)
#     client = dropbox_get_connection(admin, 'client')
#     text = 'test from view'

#     path = timezone.now().strftime('/%Y/%b/%d/deez_%I:%M%p.txt')
#     client.put_file(path, text)

#     return JsonResponse({'status': 'Ok'})


# def dropbox_edit_note(request):
#     # TEST TEST TEST
#     admin = User.objects.get(pk=1)
#     client = dropbox_get_connection(admin, 'client')
#     text = 'test from edit note view'

#     path = '/2016/feb/29/deez_09:27AM (1).txt'

#     client.put_file(path, text, overwrite=True)

#     return JsonResponse({'status': 'Ok'})


# def format_date(clear_str, res_dict=None):
#     if not res_dict:
#         res_dict = {}

#     file_info = clear_str.split('/')

#     try:
#         res_dict[file_info[1]][file_info[2]][file_info[3]].append(file_info[4])
#     except:
#         if file_info[1] in res_dict:
#             if file_info[2] in res_dict[file_info[1]]:
#                 res_dict[file_info[1]][file_info[2]].update({
#                     file_info[3]: [file_info[4]]
#                 })
#             else:
#                 res_dict[file_info[1]].update({
#                     file_info[2]: {
#                         file_info[3]: [file_info[4]]
#                     }})
#         else:
#             res_dict.update({
#                 file_info[1]: {
#                     file_info[2]: {
#                         file_info[3]: [file_info[4]]
#                     }
#                 }
#             })

#     return res_dict




# FILTER_REGEXP = [
#     '(?:19|20)\d\d',
#     settings.REGEXP_FOR_MONTH_FOLDERS,
#     '\d\d',
# ]


# def dropbox_filter_folder(path, step=1) {
#     folders = dbx.files_list_folder(path).entries
#     regexp = FILTER_REGEXP[step]
#     for folder in folders:
#         if isinstance(folder, FolderMetadata):
#             if re.match(regexp, folder.path_lower.split('/')[step]):
#                 if step == 3:
#                     res.append(folder.path_lower)
#                 dropbox_filter_folder(folder.path_lower, step++)
# }


    # years = []
    # monthes = []
    # days = []
    # for clean_first_folder in dirty_years_folders:
    #     if isinstance(clean_first_folder, FolderMetadata):
    #         if re.match('(?:19|20)\d\d', clean_first_folder.path_lower.split('/')[1]):
    #             years.append(clean_first_folder.path_lower)

    # for folder in years:
    #     all_files = dbx.files_list_folder(folder).entries
    #     for month in all_files:
    #         if isinstance(month, FolderMetadata):
    #             if re.match('{}'.format('|'.join(settings.FOLDER_NAME_MONTH)), month.path_lower.split('/')[2]):
    #                 monthes.append(month.path_lower)

    # for folder in monthes:
    #     all_files = dbx.files_list_folder(folder).entries
    #     for day in all_files:
    #         if isinstance(day, FolderMetadata):
    #             if re.match('\d\d', day.path_lower.split('/')[3]):
    #                 days.append(day.path_lower)

    # return JsonResponse({'days': days})
