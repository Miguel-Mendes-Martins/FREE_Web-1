from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.conf import settings
from django.http import HttpResponse
from django.views import View
from pydoc import locate

class LoginView(auth_views.LoginView):
    template_name = 'free/login.html'

        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        auth_backends = []
        for b in settings.AUTHENTICATION_BACKENDS:
            try:           
                my_class = locate(b)
                auth_backends.append({ 'classname':my_class.name, 'name': my_class.name.replace('-', " ").upper()})
            except:
                pass
        context['back_ends'] = auth_backends
        return context

class AuthenticationErrorView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('Error autheticating')

class LogoutView(auth_views.LogoutView):
    pass
