from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView


class MainView(TemplateView):
    template_name = 'notes/main.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_active:
            return redirect(reverse('auth:logout'))
        return super(MainView, self).dispatch(request, *args, **kwargs)
