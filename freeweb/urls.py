"""freeweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from django.views.i18n import JavaScriptCatalog
#from quiz_pendulum.quiz_structure.admin import pendquiz_admin_site
from pendulum_quiz.admin import pendquiz_admin_site
from montecarlo_quiz.admin import mcquiz_admin_site

urlpatterns = [
    path('', include('free.urls')),
    path('admin/', admin.site.urls, name='administration'),
    path('jsi18n/',JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('summernote/', include('django_summernote.urls')),
    path('', include('social_django.urls', namespace='social')),
    path('', include('free.videoConfig.urls')),
    path('', include('free.userAdmin.urls')),
    path('mc_quiz/',include('mc_quiz.quiz_mc.urls'),name='mc_quiz'),
    path('pendulum_quiz/',include('pendulum_quiz.urls'),name='pendulum_quiz'),
    path('montecarlo_quiz/',include('montecarlo_quiz.urls'),name='montecarlo_quiz'),
    path('lti/', include('lti_provider.urls')),
    path('pendquiz-admin/', pendquiz_admin_site.urls),
    path('mcquiz-admin/', mcquiz_admin_site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
