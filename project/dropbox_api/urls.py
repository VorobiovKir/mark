from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^auth_start/?$', views.dropbox_auth_start,
        name='auth_start'),
    url(r'^auth_finish/?$', views.dropbox_auth_finish,
        name='auth_finish'),
]
