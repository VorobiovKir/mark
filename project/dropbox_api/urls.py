from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^auth_start/?$', views.dropbox_auth_start,
        name='auth_start'),
    url(r'^auth_finish/?$', views.dropbox_auth_finish,
        name='auth_finish'),
    url(r'^get_notes/$', views.dropbox_get_notes,
        name='get_notes'),
    url(r'^get_notes_alt/$', views.dropbox_get_notes_version_alt,
        name='get_notes_alt')
]
