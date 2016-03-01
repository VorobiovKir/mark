from django.shortcuts import redirect
from django.views.generic import FormView, RedirectView
from django.contrib.auth import (login as app_login,
                                 logout as app_logout)
from django.contrib.auth import authenticate
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect


from .forms import AuthenticationForm, RegistrationForm


class LoginView(FormView):
    """Login View

        View allows User enter to system. If User successfully login
    system check if user is active and has access token, if User hasn't
    system redirect User to Dropbox authorization to get access_token, if
    User is active and has access token User redirect on the main page

    Extends:
        django.views.generic.FormView

    Variables:
        template_name {str} -- template
        form_class {obj} -- form for view

    """
    template_name = 'authorization/login.html'
    form_class = AuthenticationForm

    def form_valid(self, form):
        """Login form valid

        Login User, Check User's active status, if User is active
        redirect on the main page, another redirect on Dropbox
        authorization to get access_token

        """
        user = form.get_user()
        app_login(self.request, user)
        if user.is_active:
            return super(LoginView, self).form_valid(form)
        else:
            return HttpResponseRedirect(reverse('dropbox:auth_start'))


class RegisterView(FormView):
    """Registration View

        View allows User registration. If User successfully registration
    User redirect on Dropbox authorization for get access token, if User
    got token, this token save in DB in Drpopbox Model, than User redirect
    on the main page

    Extends:
        django.views.generic.FormView

    Variables:
        template_name {str} -- template
        success_url {str} -- url if User successfully registrated
        form_class {obj} -- form for view

    """
    form_class = RegistrationForm
    template_name = 'authorization/registration.html'

    def form_valid(self, form):
        """Registration form Valid

        Save User in DB, than login, than redirect on Dropbox authorization
        to get access token

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

    If User is authenticated, System Logout User

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
