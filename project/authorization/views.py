from django.shortcuts import redirect
from django.views.generic import FormView, RedirectView
from django.contrib.auth import (login as app_login,
                                 logout as app_logout)
from django.contrib.auth import authenticate
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect


from .forms import AuthenticationForm, RegistrationForm


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
            return HttpResponseRedirect(reverse('dropbox:auth_start'))


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
            return redirect(reverse('dropbox:auth_start'))

        # return redirect(reverse('auth:register'))
        return super(RegistrationForm, self).form_valid(form)


class LogoutView(RedirectView):
    """Logout View

    If User is authenticated doing log out User from site

    Extends:
        django.views.generic.RedirectView

    Variables:
        url {str} -- redirect if success logout

    """
    url = reverse_lazy('auth:login')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            app_logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)
