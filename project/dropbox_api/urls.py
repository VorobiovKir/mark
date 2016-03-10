from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^auth_start/?$', views.dropbox_auth_start,
        name='auth_start'),
    url(r'^auth_finish/?$', views.dropbox_auth_finish,
        name='auth_finish'),
    # url(r'^get_notes/$', views.dropbox_get_notes,
    #     name='get_notes'),
    url(r'^get_notes_alt/$', views.dropbox_get_notes_version_alt,
        name='get_notes_alt'),
    url(r'^get_notes_final/$', views.dropbox_get_notes_version_search,
        name='get_notes_final'),

    url(r'^create_or_edit_note/$', views.dropbox_create_or_edit_note,
        name='create_or_edit_note'),
    url(r'^change_meta_note/$', views.dropbox_change_meta_note,
        name='change_meta_note'),

    # url(r'^get_note/$', views.dropbox_get_note, name='get_note'),

    url(r'^search/$', views.dropbox_search, name='search'),
    # url(r'^edit_note/$', views.dropbox_edit_note, name='edit'),
    url(r'^get_meta_files/$', views.dropbox_get_meta_files,
        name='get_meta_files'),
    url(r'^add_or_del_meta_files/$', views.dropbox_add_or_del_meta_files,
        name='add_or_del_meta_files'),

    url(r'^format_to_date/$', views.format_list_to_date,
        name='format_to_date'),

    url(r'^upload_file/$', views.dropbox_upload_file,
        name='upload_file'),
]
