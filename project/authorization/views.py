from django.shortcuts import render, redirect
from django.views.generic import FormView, RedirectView
from django.contrib.auth import (login as app_login,
                                 logout as app_logout)
from django.contrib.auth import authenticate
from django.conf import settings
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import (HttpResponseRedirect, HttpResponse,
                         HttpResponseForbidden)
from django.contrib.auth.models import User

from dropbox import DropboxOAuth2Flow
from dropbox import oauth

from .forms import AuthenticationForm, RegistrationForm
from .models import Dropbox


class LoginView(FormView):
    template_name = 'authorization/login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('notes:main')

    def form_valid(self, form):
        user = form.get_user()
        app_login(self.request, user)
        if user.is_active:
            return super(LoginView, self).form_valid(form)
        else:
            return HttpResponseRedirect(reverse('auth:dropbox_auth_start'))


class RegisterView(FormView):
    """Registration View

        View allows User registration. If User successfully registration
    in profile.models.profile create new field with User's slug, activation key
    and expire day of this key. View generate activation key and send his on
    User Email for confirmed.

    Extends:
        django.views.generic.FormView

    Variables:
        template_name {str} -- template
        success_url {str} -- url if User successfully registrated
        form_class {obj} -- form for view

    Methods:
        form_valid -- Save User, Create Profile[slug],
            Generate activation key and expire date for confirm email.
            Send on User's email confirm letter

    """
    form_class = RegistrationForm
    template_name = 'authorization/registration.html'

    def form_valid(self, form):
        """Form Valid

        If form valid User save.

        Return:
            Redirect to Dropbox Api for get access token

        """
        form.save()
        user = authenticate(username=form.cleaned_data.get('username'),
                            password=form.cleaned_data.get('password1'))

        if user is not None:
            app_login(self.request, user)
            return redirect(reverse('auth:dropbox_auth_start'))

        # return redirect(reverse('auth:register'))
        return super(RegistrationForm, self).form_valid(form)


def get_dropbox_auth_flow(web_app_session):
    redirect_uri = '{}auth/dropbox_auth_finish/'.format(settings.SITE_PATH)
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
            '{}dropbox_auth_start/'.format(settings.SITE_PATH))
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
        # user.backend = settings.AUTHENTICATION_BACKENDS[0]
        # app_login(request, user)
    return redirect(reverse('notes:main'))
