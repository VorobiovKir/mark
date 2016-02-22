from django.conf.urls import url

from .views import LoginView
from . import views

urlpatterns = [
    url(r'^login/', LoginView.as_view(), name='login'),
    url(r'^dropbox_auth_start/?$', views.dropbox_auth_start),
    # url(r'^dropbox_auth_finish/?$', views.dropbox_auth_finish),
]
