from django.conf.urls import url

from .views import LoginView, RegisterView
from . import views

urlpatterns = [
    url(r'^login/', LoginView.as_view(), name='login'),
    url(r'^register/', RegisterView.as_view(), name='register'),
    url(r'^dropbox_auth_start/?$', views.dropbox_auth_start,
        name='dropbox_auth_start'),
    url(r'^dropbox_auth_finish/?$', views.dropbox_auth_finish,
        name='dropbox_auth_finish'),
    # url(r'^dropbox_auth_finish/?$', views.dropbox_auth_finish),
]
