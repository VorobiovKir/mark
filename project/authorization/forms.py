from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import ugettext_lazy as _


class AuthenticationForm(AuthenticationForm):
    """ Authentication Form

    Authentication form for user

    Model:
        django.contrib.auth.models.User

    Extends:
        django.contrib.auth.forms.AuthenticationForm

    Variables:
        username {string} -- user name
        password {string} -- user password

    """
    def confirm_login_allowed(self, user):
        """confirm login allowed

        remove default check on user active, cause system doing
        this revision after login
        """
        pass

    class Meta:
        model = User
        fields = ['username', 'password']


class RegistrationForm(UserCreationForm):
    """ Registration Form

    Registration form for new user

    Model:
        django.contrib.auth.models.User

    Extends:
        django.contrib.auth.forms.UserCreationForm

    Variables:
        email {string} -- required, unique, user email
        username {string} -- user name, unique
        password1 {string} -- user password
        password2 {string} -- confirmed user password

    """
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2']

    def clean_email(self):
        """Registration clean email

        Check on unique User email

        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Duplicate email'))
        return email

    def save(self, commit=True):
        """registration save

        User's active satus False

        """
        user = super(RegistrationForm, self).save(commit=False)
        if commit:
            user.is_active = False
            user.save()
        return user
