import re

from django.shortcuts import redirect
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import (HttpResponseRedirect, HttpResponse,
                         HttpResponseForbidden)
from django.contrib.auth.models import User
from django.http import JsonResponse

from dropbox import DropboxOAuth2Flow, oauth, dropbox
from dropbox.files import FileMetadata, FolderMetadata

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

        return HttpResponseRedirect(
            '{}dropbox/auth/login'.format(settings.SITE_PATH))
        raise e
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
    try:
        access_token = \
            User.objects.get(pk=1).dropbox.access_token
    except:
        pass

    # client = dropbox.client.DropboxClient(access_token)
    dbx = dropbox.Dropbox(access_token)
    all_files = dbx.files_list_folder('', recursive=True).entries
    files = []
    pattern = settings.REGEX_FILES
    for dirty_file in all_files:
        if isinstance(dirty_file, FileMetadata):
            if re.match(pattern, dirty_file.path_lower):
                files.append(dirty_file.path_lower)

    return JsonResponse({'paths': files, 'length': len(all_files)})


def dropbox_create_note(request):
    pass


def dropbox_edit_note(request):
    pass


def dropbox_get_notes_version_alt(request):
    try:
        access_token = \
            User.objects.get(pk=1).dropbox.access_token
    except:
        pass

    # client = dropbox.client.DropboxClient(access_token)
    dbx = dropbox.Dropbox(access_token)
    all_files = dbx.files_list_folder('').entries

    FOLDER_NAME_MONTH = ['jan', 'feb', 'mar', 'apr', 'may', 'june', 'july',
                     'aug', 'sept', 'oct', 'nov', 'dec']

    years = []
    monthes = []
    days = []
    for folder in all_files:
        if isinstance(folder, FolderMetadata):
            if re.match('(?:19|20)\d\d', folder.path_lower.split('/')[1]):
                years.append(folder.path_lower)

    for folder in years:
        all_files = dbx.files_list_folder(folder).entries
        for month in all_files:
            if isinstance(month, FolderMetadata):
                if re.match('{}'.format('|'.join(FOLDER_NAME_MONTH)), month.path_lower.split('/')[2]):
                    monthes.append(month.path_lower)

    for folder in monthes:
        all_files = dbx.files_list_folder(folder).entries
        for day in all_files:
            if isinstance(day, FolderMetadata):
                if re.match('\d\d', day.path_lower.split('/')[3]):
                    days.append(day.path_lower)

    return JsonResponse({'days': days})
