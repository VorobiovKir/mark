from django.shortcuts import redirect
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import (HttpResponseRedirect, HttpResponse,
                         HttpResponseForbidden)

from dropbox import DropboxOAuth2Flow
from dropbox import oauth

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
        raise e
    except oauth.ProviderException, e:
        raise e

    if access_token:
        user = request.user
        user.is_active = True
        user.save()
        dropbox = Dropbox.objects.get_or_create(user=user)[0]
        dropbox.access_token = access_token
        dropbox.save()
    return redirect(reverse('notes:main'))
