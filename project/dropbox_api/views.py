import re

from django.shortcuts import redirect
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import (HttpResponseRedirect, HttpResponse,
                         HttpResponseForbidden)
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone

from dropbox import DropboxOAuth2Flow, oauth, dropbox
from dropbox.files import FileMetadata, FolderMetadata
from dropbox.client import DropboxClient

from .models import Dropbox


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


def dropbox_get_notes(request):
    # TEST TEST TEST
    admin = User.objects.get(pk=1)

    dbx = dropbox_get_connection(admin)

    all_files = dbx.files_list_folder('', recursive=True).entries
    files = []
    pattern = settings.REGEX_FILES
    for dirty_file in all_files:
        if isinstance(dirty_file, FileMetadata):
            if re.match(pattern, dirty_file.path_lower):
                files.append(dirty_file.path_lower)

    return JsonResponse({'paths': files, 'length': len(all_files)})


def dropbox_create_note(request):
    # TEST TEST TEST
    text = 'test from view'
    admin = User.objects.get(pk=1)
    client = dropbox_get_connection(admin, 'client')

    path = timezone.now().strftime('/%Y/%b/%d/deez_%I:%M%p.txt')
    client.put_file(path, text)

    return JsonResponse({'status': 'Ok'})


def dropbox_edit_note(request):
    # TEST TEST TEST
    admin = User.objects.get(pk=1)
    client = dropbox_get_connection(admin, 'client')
    text = 'test from edit note view'
    path = '/2016/feb/29/deez_09:27AM (1).txt'

    client.put_file(path, text, overwrite=True)

    return JsonResponse({'status': 'Ok'})


def dropbox_get_file(request):
    # TEST TEST TEST
    admin = User.objects.get(pk=1)

    client = dropbox_get_connection(admin, 'client')
    path = request.GET.get('path')

    with client.get_file(path) as f:
        result = f.read()

    return JsonResponse({'content': result})


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


def dropbox_get_notes_version_search(request):
    # TEST TEST TEST
    admin = User.objects.get(pk=1)

    dbx = dropbox_get_connection(admin)

    matches = dbx.files_search('', 'deez').matches
    result = []
    regex = settings.REGEX_FILES

    for search_match in matches:
        if isinstance(search_match.metadata, FileMetadata):
            if re.match(regex, search_match.metadata.path_lower):
                result.append(search_match.metadata.path_lower)

    return JsonResponse({'days': result})

def dropbox_get_notes_version_alt(request):
    # TEST TEST TEST
    admin = User.objects.get(pk=1)

    dbx = dropbox_get_connection(admin)

    days = []
    REGEXP_FOR_MONTH_FOLDERS = '{}'.format('|'.join(settings.FOLDER_NAME_MONTH))

    dirty_years_folders = dbx.files_list_folder('').entries
    for clean_years_folder in dirty_years_folders:
        if isinstance(clean_years_folder, FolderMetadata):
            if re.match('(?:19|20)\d\d',
                clean_years_folder.path_lower.split('/')[1]):

                dirty_month_folders = \
                    dbx.files_list_folder(clean_years_folder.path_lower).entries
                for clean_month_folder in dirty_month_folders:
                    if isinstance(clean_month_folder, FolderMetadata):
                        if re.match(REGEXP_FOR_MONTH_FOLDERS,
                            clean_month_folder.path_lower.split('/')[2]):

                            dirty_days_folders = \
                                dbx.files_list_folder(clean_month_folder.path_lower).entries
                            for clean_days_folder in dirty_days_folders:
                                if isinstance(clean_days_folder, FolderMetadata):
                                    if re.match('\d\d',
                                        clean_days_folder.path_lower.split('/')[3]):

                                        dirty_files = \
                                            dbx.files_list_folder(clean_days_folder.path_lower).entries
                                        for clean_file in dirty_files:
                                            if isinstance(clean_file, FileMetadata):
                                                if re.match('deez_(.*)\.txt$',
                                                    clean_file.path_lower.split('/')[4]):

                                                    days.append(clean_file.path_lower)

    return JsonResponse({'days': days})


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
