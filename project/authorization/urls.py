from django.conf.urls import url

from .views import LoginView, RegisterView, LogoutView
# from . import views

urlpatterns = [
    url(r'^login/', LoginView.as_view(), name='login'),
    url(r'^logout/', LogoutView.as_view(), name='logout'),
    url(r'^register/', RegisterView.as_view(), name='register'),
]
