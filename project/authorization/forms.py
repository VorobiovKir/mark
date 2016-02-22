# from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import ugettext_lazy as _


class AuthenticationForm(AuthenticationForm):
    """ Authentication Form

    Authentication form for user.

    Model:
        django.contrib.auth.models.User

    Extends:
        django.contrib.auth.forms.AuthenticationForm

    Variables:
        username {string} -- user name
        password {string} -- user password

    """

    def confirm_login_allowed(self, user, *args, **kwargs):
        if not user.is_active:
            print 'not active'

    class Meta:
        model = User
        fields = ['username', 'password']
