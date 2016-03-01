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
        name='get_notes_alt'),
    url(r'^search/$', views.dropbox_search, name='search'),
    url(r'^get_file/$', views.dropbox_get_file, name='get_file'),
    url(r'^get_notes_final/$', views.dropbox_get_notes_version_search,
        name='get_notes_final'),
    url(r'^create_note/$', views.dropbox_create_note, name='create'),
    url(r'^edit_note/$', views.dropbox_edit_note, name='edit'),
]
