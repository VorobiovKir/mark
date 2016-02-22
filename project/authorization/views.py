from django.shortcuts import render
from django.views.generic import FormView, RedirectView
from django.contrib.auth import (login as app_login,
                                 logout as app_logout)
from django.conf import settings
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect, HttpResponse

from dropbox import DropboxOAuth2Flow
from dropbox import oauth

from .forms import AuthenticationForm, RegistrationForm


class DropBoxAuthView(RedirectView):
    url = reverse_lazy('auth:login')


class LoginView(FormView):
    template_name = 'authorization/login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('notes:main')

    def form_valid(self, form):
        user = form.get_user()
        if user.is_active:
            app_login(self.request, user)
            return super(LoginView, self).form_valid(form)
        else:
            return HttpResponseRedirect(reverse('auth:dropbox_auth'))


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

        If form valid User save in database with his profile.
        Generate Activation key with expire date.
        For User's email sended confirmation letter

        Return:
            Redirect

        """
        form.save()

        user_email = form.cleaned_data['email']

        activation_key = self.generate_activation_key(user_email)
        key_expires = self.generate_key_expires(settings.KEY_EXPIRE_TERM)

        user = User.objects.get(email=user_email)

        slug = self.create_slug(user)

        new_profile = Profile(
            user=user,
            activation_key=activation_key,
            key_expires=key_expires,
            slug=slug
        )
        new_profile.save()

        return render(
            self.request,
            settings.REGISTRATION_TEMPLATES['thanks'],
            context={
                'username': user.username,
                'email': user.email
            }
        )


def get_dropbox_auth_flow(web_app_session):
    redirect_uri = "http://127.0.0.1:8000"
    return DropboxOAuth2Flow(
        settings.DROPBOX_APP_KEY, settings.DROPBOX_APP_SECRET,
        redirect_uri, web_app_session, "dropbox-auth-csrf-token")


# URL handler for /dropbox-auth-start
def dropbox_auth_start(request):
    authorize_url = get_dropbox_auth_flow(request.session).start()
    return HttpResponseRedirect(authorize_url)


# # URL handler for /dropbox-auth-finish
# def dropbox_auth_finish(web_app_session, request):
#     try:
#         access_token, user_id, url_state = \
#                 get_dropbox_auth_flow(web_app_session).finish(
#                     request.query_params)
#     except oauth.BadRequestException, e:
#         return HttpResponse(status=400)
#     except oauth.BadStateException, e:
#         # Start the auth flow again.
#         return HttpResponseRedirect("/dropbox-auth-start")
#     except oauth.CsrfException, e:
#         return HttpResponse(status=403)
#     except oauth.NotApprovedException, e:
#         return HttpResponseRedirect("/home")
#     except e:
#         return HttpResponse(status=403)


# def get_dropbox_auth_flow(web_app_session):
#     redirect_uri = "http://www.mydomain.com"
#     return DropboxOAuth2Flow('blahblahblah', 'blehblehbleh', redirect_uri, web_app_session, "dropbox-auth-csrf-token")

# # URL handler for /dropbox-auth-start
# def dropbox_auth_start(request):
#     authorize_url = get_dropbox_auth_flow(request.session).start()
#     return HttpResponseRedirect(authorize_url)

# # URL handler for /dropbox-auth-finish
# def dropbox_auth_finish(request):
#     try:
#         access_token, user_id, url_state = get_dropbox_auth_flow(request.session).finish(request.GET)
#     except DropboxOAuth2Flow.BadRequestException, e:
#         http_status(400)
#     except DropboxOAuth2Flow.BadStateException, e:
#         # Start the auth flow again.
#         return HttpResponseRedirect("http://www.mydomain.com/dropbox_auth_start")
#     except DropboxOAuth2Flow.CsrfException, e:
#         return HttpResponseForbidden()
#     except DropboxOAuth2Flow.NotApprovedException, e:
#         raise e
#     except DropboxOAuth2Flow.ProviderException, e:
#         raise e
