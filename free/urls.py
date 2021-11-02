from free.views.api import ChangeExecutionStatus, ExecutionQueue, NextExecution
from free.views.base import LoginView, LogoutView
from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


from . import views

from .views.layoutpages import ProtocolsView, ExecutionsView, ExecutionView
# Helper function to generate API documentation
schema_view = get_schema_view(
   openapi.Info(
      title="FREE API",
      default_version='v1',
      description="Documentation for FREE API endpoints",
      contact=openapi.Contact(email="kurispav@fjfi.cvut.cz"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

app_name = 'free'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.LogoutView.as_view(), name='logout'),

    # API DOCUMENTATION
    re_path(r'^free-api(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^api/swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^api/redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # PAGES
    path('protocols', ProtocolsView.as_view(), name='protocols'),
    path('executions', ExecutionsView.as_view(), name='executions'),
    path('new_execution', ExecutionView.as_view(), name='new_execution'),

    path('experiment/<slug:slug>', views.ExperimentView.as_view(), name='experiment'),
    path('experiment/<slug:slug>/<int:execution>', views.ExperimentExecutionView.as_view(), name='experiment-execution'),

    # REST API
    path('api/v1/experiments', views.ExperimentListAPI.as_view(), name='api-experiment-list'),

    path('api/v1/execution', views.ExecutionConfigure.as_view(), name='api-execution-configure' ),
    path('api/v1/execution/<int:id>', views.ExecutionRetrieveUpdateDestroy().as_view(), name='api-execution'),
    path('api/v1/execution/<int:id>/start', views.ExecutionStart.as_view(), name='api-execution-start'),
    path('api/v1/execution/<int:id>/status', views.ChangeExecutionStatus.as_view(), name='api-execution-status-change'),
    path('api/v1/execution/<int:id>/result', views.ResultList.as_view(), name='api-result-list'),
    path('api/v1/execution/<int:id>/result/<int:last_id>', views.ResultListFiltered.as_view(), name='api-result-list-filtered'),
    
    path('api/v1/apparatus/<int:id>', views.AppratusView.as_view(), name='api-apparatus-view'),
    path('api/v1/apparatus/<int:id>/nextexecution', views.NextExecution.as_view(), name='api-execution-next'),
    path('api/v1/apparatus/<int:id>/queue', views.ExecutionQueue.as_view(), name='api-execution-queue'),

    path('api/v1/result', views.AddResult.as_view(), name='api-result-add'),
]