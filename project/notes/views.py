from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView


class MainView(TemplateView):
    """Main View

    Template view, checked if user is active, if not redirect to
    login page

    Extends:
        from django.views.generic import TemplateView

    Variables:
        template_name {str} -- name of main page
    """
    template_name = 'notes/main.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_active:
            return redirect(reverse('welcome'))
        return super(MainView, self).dispatch(request, *args, **kwargs)
