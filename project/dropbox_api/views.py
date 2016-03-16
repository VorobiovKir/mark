import re
import json

from django.shortcuts import redirect
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import (HttpResponseRedirect, HttpResponse,
                         HttpResponseForbidden, HttpResponseServerError, FileResponse)
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone

from dropbox import oauth, dropbox
from dropbox.files import FileMetadata, FolderMetadata
from dropbox.client import DropboxOAuth2Flow, DropboxClient

from generic import custom_funcs

from .models import Dropbox

import logging
log = logging.getLogger(__name__)


# --------------------- AUTHORIZATION VIEWS ---------------------------
def get_dropbox_auth_flow(web_app_session):
    """Get dropbox auth flow

    Addition method for dropbox authorization, get application key, and
    secret key, session, redirect url

    Return DropboxOAuth2Flow object for dropbox authorization
    """
    redirect_uri = '{}dropbox/auth_finish/'.format(settings.SITE_PATH)
    return DropboxOAuth2Flow(
        settings.DROPBOX_APP_KEY, settings.DROPBOX_APP_SECRET,
        redirect_uri, web_app_session, "dropbox-auth-csrf-token")


def dropbox_auth_start(request):
    """Dropbox auth session start

    Start session to authorizate in dropbox system

    Returns:
        redirect to dropbox auth system
    """
    authorize_url = get_dropbox_auth_flow(request.session).start()
    return HttpResponseRedirect(authorize_url)


def dropbox_auth_finish(request):
    """Dropbox authorization finish

    Final method who get from dropbox object, with authorization
    information. In successfully case we get access token
    """
    try:
        res = get_dropbox_auth_flow(request.session).finish(request.GET)
        access_token, user_id, url_state = res
    except oauth.BadRequestException, e:
        log.error("{}: Oauth bad request {}".format(
            timezone.now().strftime('[%Y/%m/%d] ---  %H:%M:%S'), e))
        return HttpResponse(status=400)
    except oauth.BadStateException, e:
        log.error("{}: Bad state exception {}".format(
            timezone.now().strftime('[%Y/%m/%d] ---  %H:%M:%S'), e))
        return redirect(reverse('dropbox:auth_start'))
    except oauth.CsrfException, e:
        log.error("{}: Oauth Csrf error {}".format(
            timezone.now().strftime('[%Y/%m/%d] ---  %H:%M:%S'), e))
        return HttpResponseForbidden()
    except oauth.NotApprovedException, e:
        log.error("{}: Oauth not approved exception {}".format(
            timezone.now().strftime('[%Y/%m/%d] ---  %H:%M:%S'), e))
        return HttpResponseRedirect(reverse('auth:logout'))
    except oauth.ProviderException, e:
        log.error("{}: Oauth provider exception {}".format(
            timezone.now().strftime('[%Y/%m/%d] ---  %H:%M:%S'), e))
        raise e

    if access_token:
        log.info("{}: Get Access Token {}".format(
            timezone.now().strftime('[%Y/%m/%d] ---  %H:%M:%S'),
            access_token))
        user = request.user
        user.is_active = True
        user.save()
        dropbox_profile = Dropbox.objects.get_or_create(user=user)[0]
        dropbox_profile.access_token = access_token
        dropbox_profile.save()
        return redirect(reverse('notes:main'))

    log.error("{}: Something going wrong").format(
        timezone.now().strftime('[%Y/%m/%d] ---  %H:%M:%S'))
    return redirect(reverse('auth:logout'))
# ------------------------------------------------------------------


# --------------------- GET API VIEWS ---------------------------
def dropbox_get_connection(user, type_connection='dbx'):
    """Dropbox get connection

    Method return dropbox api object

    Arguments:
        user {object} -- current User

    Keyword Arguments:
        type_connection {str} -- quering api type (default: {'dbx'})

    Returns:
        [object] -- dropbox api object
    """
    access_token = dropbox_get_access_token(user)

    if type_connection == 'dbx':
        return dropbox.Dropbox(access_token)
    elif type_connection == 'client':
        return DropboxClient(access_token)


def dropbox_get_access_token(user):
    """Dropbox get access token

    Method return access token, if User doesn't have access token,
    method change User active status to False and doing logout User from
    auth system

    Arguments:
        user {object} -- current User

    Returns:
        [string] -- access token
    """
    try:
        access_token = \
            User.objects.get(pk=user.pk).dropbox.access_token
    except:
        user.is_active = False
        user.save()
        return HttpResponseRedirect(reverse('auth:logout'))

    return access_token
# -----------------------------------------------------------


# --------------------- GET NOTES ---------------------------
def dropbox_get_notes_version_search(request):
    """Dropbox get notes by search

    Get All Notes from dropbox by dropboxs search system

    Returns:
        [json object] -- Object has all user notes, formating by
        information, date and no formating notes
    """
    user = request.user
    dbx = dropbox_get_connection(user)
    client = dropbox_get_connection(user, 'client')

    notes = get_notes_by_search(dbx)
    notes = custom_funcs.sorted_by_time(notes)

    date_notes = {}
    for note in notes:
        date_notes = custom_funcs.format_date(note, date_notes)

    full_info_notes = custom_funcs.format_get_list_full_info(notes, client)
    # full_info_notes = custom_funcs.format_get_dict_full_info(result, client)

    return JsonResponse({
        'format_result': date_notes,
        'result': full_info_notes,
        'order': notes
    })


def dropbox_get_notes_version_alt(request):
    """Dropbox get notes by Regexp

    Get All Notes from dropbox by custom Regexp search system

    Returns:
        [json object] -- Object has all user notes, formating by
        information, date and no formating notes
    """
    user = request.user
    dbx = dropbox_get_connection(user)
    client = dropbox_get_connection(user, 'client')

    notes = get_notes_by_exceptions(dbx)
    notes = custom_funcs.sorted_by_time(notes)

    date_notes = {}
    for note in notes:
        date_notes = custom_funcs.format_date(note, date_notes)

    full_info_notes = custom_funcs.format_get_list_full_info(notes, client)

    return JsonResponse({
        'format_result': date_notes,
        'result': full_info_notes,
        'order': notes
    })


def get_notes_by_exceptions(dbx):
    """Get notes by exception

    Addition method who find notes by regexp

    Example:
        '/2016/jan/10/deez_nameOfProject_nameOfTags_time.txt'

    Arguments:
        dbx {object} -- dropbox api object

    Returns:
        [list] -- all notes path
    """
    REGEXP_FOR_MONTH_FOLDERS = '{}'.format(
        '|'.join(settings.FOLDER_NAME_MONTH))

    clean_years = []
    clean_month = []
    clean_days = []
    clean_files_path = []

    dirty_years_folders = dbx.files_list_folder('').entries
    for dirty_years_folder in dirty_years_folders:
        if isinstance(dirty_years_folder, FolderMetadata):
            if re.match('(?:19|20)\d\d', dirty_years_folder.name):
                clean_years.append(dirty_years_folder.path_lower)

    for year_folder_path in clean_years:
        dirty_month_folders = dbx.files_list_folder(year_folder_path).entries

        for dirty_month_folder in dirty_month_folders:
            if isinstance(dirty_month_folder, FolderMetadata):
                if re.match(REGEXP_FOR_MONTH_FOLDERS,
                            dirty_month_folder.name, re.IGNORECASE):
                    clean_month.append(dirty_month_folder.path_lower)

    for month_folder_path in clean_month:
        dirty_days_folders = dbx.files_list_folder(month_folder_path).entries

        for dirty_days_folder in dirty_days_folders:
            if isinstance(dirty_days_folder, FolderMetadata):
                if re.match('\d\d', dirty_days_folder.name):
                    clean_days.append(dirty_days_folder.path_lower)

    for days_folder_path in clean_days:
        dirty_notes_path = dbx.files_list_folder(days_folder_path).entries

        for dirty_note_path in dirty_notes_path:
            if isinstance(dirty_note_path, FileMetadata):
                if re.match('deez_(.*)_(.*)_(.*)\.txt$', dirty_note_path.name):
                    clean_files_path.append(dirty_note_path.path_lower)

    return clean_files_path


def get_notes_by_search(dbx):
    """Get notes by api search

    Addition method who find notes by search

    Example:
        '/2016/jan/10/deez_nameOfProject_nameOfTags_time.txt'

    Arguments:
        dbx {object} -- dropbox api object

    Returns:
        [list] -- all notes path
    """
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
    """Dropbox create/edit note method

    Method allows create or edit note

    Returns:
        [object] -- Object contain all information about target note
    """
    user = request.user
    client = dropbox_get_connection(user, 'client')

    params = json.loads(request.body)

    text = params.get('text')
    note_path = params.get('path')
    action = params.get('action')
    overwrite = (action == 'edit')

    if action == 'create':
        project = params.get('project', settings.DROPBOX_DEFAULT_PROJECT)
        tag = params.get('tag', settings.DROPBOX_DEFAULT_TAG)
        note_path = \
            timezone.now().strftime(
                '/%Y/%b/%d/deez_{}_{}_%I:%M%p.txt').format(project, tag)

        i = 1
        request_note_path = note_path
        while client.search(*note_path.rsplit('/', 1)):
            note_path = '{}({}).txt'.format(request_note_path[:-4], i)
            i += 1

    if not note_path:
        return HttpResponseServerError('Bad request')

    client.put_file(note_path, text, overwrite=overwrite)

    return JsonResponse({
        'res': 'Success',
        'obj': {
            'path': note_path,
            'project': note_path.rsplit('/', 1)[-1].split('_')[1],
            'tag': note_path.rsplit('/', 1)[-1].split('_')[2],
            'time': note_path.split('/')[-1].split('_')[-1],
            'date':  note_path.rsplit('/', 1)[0],
            'text': text
        }})


def dropbox_change_meta_note(request):
    """Dropbox change meta note

    Method allows change name of project or tag

    """
    user = request.user
    client = dropbox_get_connection(user, 'client')

    path = request.GET.get('path')
    meta_type = request.GET.get('type')
    meta_name = request.GET.get('meta_name')
    splitted_path = path.split('/')

    if client.search('/{}/'.format('/'.join(splitted_path[1:-1])), splitted_path[-1]):
        splitted_note_name = path.split('_')

        if meta_type == 'project':
            index = 1
        elif meta_type == 'tag':
            index = 2

        splitted_note_name[index] = meta_name

        client.file_move(path, '_'.join(splitted_note_name))
        return JsonResponse({'res': 'success'})
    else:
        return HttpResponseServerError('File doesn\'t find')
# -----------------------------------------------------------


# --------------------- Search Note/Folder ------------------
def dropbox_search(request):
    # TEST TEST TEST
    # admin = User.objects.get(pk=1)
    user = request.user
    dbx = dropbox_get_connection(user)

    query = request.GET.get('query')
    result = []
    matches = dbx.files_search('', query).matches

    for search_match in matches:
        result.append(search_match.metadata.path_lower)
    return JsonResponse({'result': result})
# -----------------------------------------------------------


# --------------------- META DATA VIEWS ---------------------
def dropbox_get_meta_files(request):
    """Dropbox get meta files

    Method return all Projects or Tags name

    Returns:
        [list] -- List of name Projects or Tags
    """
    client = dropbox_get_connection(request.user, 'client')
    search_type = request.GET.get('search_type')

    if search_type:
        if search_type == 'projects':
            default_name = settings.DROPBOX_DEFAULT_PROJECT
        else:
            default_name = settings.DROPBOX_DEFAULT_TAG

        result = dropbox_get_meta_data(search_type, client)
        result = [default_name] + result

        return JsonResponse({'result': result})
    else:
        return JsonResponse({'errors': 'not valible query'})


def dropbox_get_meta_data(type_meta_data, api):
    """Dropbox get meta data

    Additional method for get all Projects or Tags name
    Get Type ('projects' or 'tags') and Return list

    Arguments:
        type_meta_data {string} -- 'projects' or 'tags'
        api {object} -- dropboxes api connection object

    Returns:
        [list] -- list of name
    """
    if type_meta_data == 'projects':
        file_name = settings.DROPBOX_PROJECTS_FILE
    elif type_meta_data == 'tags':
        file_name = settings.DROPBOX_TAGS_FILE

    if api.search(settings.DROPBOX_META_PATH, file_name):
        file_content = api.get_file(settings.DROPBOX_META_PATH + file_name)
        return filter(None, file_content.read().split('\n'))
    else:
        return []


def dropbox_add_or_del_meta_files(request):
    # TEST TEST TEST
    # admin = User.objects.get(pk=1)
    user = request.user
    client = dropbox_get_connection(user, 'client')

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


def format_list_to_date(request):
    params = json.loads(request.body)
    notes = params.get('notes')
    new_note = params.get('new_note').get('path')
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    notes = custom_funcs.format_date(new_note, notes)

    return JsonResponse({'notes': notes})


def dropbox_upload_file(request):
    # TEST TEST TEST
    # admin = User.objects.get(pk=1)
    user = request.user
    client = dropbox_get_connection(user, 'client')

    file = request.FILES.get('file')

    full_path = request.POST.get('path')
    folder = '/'.join(full_path.split('/')[:-1])
    note_name = full_path.split('/')[-1]

    if file:
        file_id = client.upload_chunk(file)

        i = 1
        first_file_name = file.name
        while client.search(folder, file.name):
            file.name = '({}){}'.format(i, first_file_name)
            i += 1

        res = client.commit_chunked_upload(
            'dropbox{}/{}'.format(folder, file.name), file_id[1])

        if res:
            file_full_path =\
                '.meta/files/{}/files_{}'.format(folder, note_name[5:])
            file_path = '/'.join(file_full_path.split('/')[:-1])
            overwrite = False
            if client.search(file_path, 'files_{}'.format(note_name[5:])):
                res = client.get_file(file_full_path).read()
                if res:
                    text = json.loads(res)
                    text.append(
                        ['{}/{}'.format(folder, file.name), file.content_type])
                    text = json.dumps(text)
                    overwrite = True
            else:
                text = json.dumps(
                    [['{}/{}'.format(folder, file.name), file.content_type]])

            client.put_file(file_full_path, text, overwrite=overwrite)

            return JsonResponse({
                'res': ['{}/{}'.format(folder, file.name), file.content_type]})

    return HttpResponseServerError('Something going wrong')


def dropbox_download_file(request):
    user = request.user
    dbx = dropbox_get_connection(user)
    client = dropbox_get_connection(user, 'client')

    path = request.GET.get('path')

    if path:
        if dbx.files_search(*path.rsplit('/', 1)):
            file = client.get_file(path)

            # header = file.getheaders()
            # content_type = header.get('Content-Type')
            # response = HttpResponse(content=file.read())
            # response['Content-Type'] = content_type
            # response['Content-Disposition'] = 'attachment; filename="foo.pdf"'

            response = FileResponse(file, 'rb')

            return response
        else:
            return HttpResponseServerError('file not found')
    else:
        return HttpResponseServerError('path not found')


def dropbox_delete_note(request):
    user = request.user
    client = dropbox_get_connection(user, 'client')

    params = json.loads(request.body)
    path = params.get('path')
    file_path, file_name = path.rsplit('/', 1)
    files_path = '.meta/files{}/files_{}'.format(file_path, file_name[5:])

    if (client.search(*files_path.rsplit('/', 1))):
        list_files = client.get_file(files_path)
        files = json.loads(list_files.read())

        for file in files:
            try:
                client.file_delete(file[0])
            except:
                pass
        client.file_delete(files_path)

    try:
        client.file_delete(path)
    except:
        return HttpResponseServerError('file is not find')

    return JsonResponse({'res': 'success'})



        # upload_file = file.read()

        # uploader = client.get_chunked_uploader(upload_file, size)
        # while uploader.offset < size:
        #     try:
        #         upload = uploader.upload_chunked()
        #     except:
        #         pass  # doing something with error
        # uploader.finish('/thisworks.txt')

    # uploader = client.get_chunked_uploader(bigFile, size)
    # print "uploading: ", size
    # while uploader.offset < size:
    #     try:
    #         upload = uploader.upload_chunked()
    #     except rest.ErrorResponse, e:
    #         pass
    #         # perform error handling and retry logic

    # uploader.finish('/bigFile.txt')


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
