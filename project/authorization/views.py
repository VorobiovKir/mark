from django.shortcuts import render
from django.views.generic import TemplateView, FormView
from django.contrib.auth import (login as app_login,
                                 logout as app_logout)

from .forms import AuthenticationForm


class WelcomeView(TemplateView):
    template_name = 'authorization/welcome.html'


class LoginView(FormView):
    template_name = 'authorization/login.html'
    form_class = AuthenticationForm

    def form_valid(self, form):
        app_login(self.request, form.get_user())
        return super(LoginView, self).form_valid(form)
