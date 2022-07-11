from free import views
from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

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
    path('apparatuses', views.ApparatusesView.as_view(), name='apparatuses'),
    path('executions/configured', views.ExecutionsConfiguredListView.as_view(), name='executions-configured'),
    path('executions/finished', views.ExecutionsFinishedListView.as_view(), name='executions-finished'),

    path('execution/create/<int:apparatus_id>/<int:protocol_id>', views.CreateExecutionView.as_view(), name='execution-create'),
    path('execution/<int:pk>', views.ExecutionView.as_view(), name='execution'),

    # REST API
    path('api/v1/version', views.Version.as_view(), name='api-version'),
    path('api/v1/apparatus_types', views.ApparatusTypeListAPI.as_view(), name='api-apparatus_type-list'),

    path('api/v1/execution', views.ExecutionConfigure.as_view(), name='api-execution-configure' ),
    path('api/v1/execution/<int:id>', views.ExecutionRetrieveUpdateDestroy().as_view(), name='api-execution'),
    path('api/v1/execution/<int:id>/name', views.ExecutionUpdateName.as_view(), name='api-execution-update-name'),
    path('api/v1/execution/<int:id>/start', views.ExecutionStart.as_view(), name='api-execution-start'),
    path('api/v1/execution/<int:id>/status', views.ChangeExecutionStatus.as_view(), name='api-execution-status-change'),
    path('api/v1/execution/<int:id>/result', views.ResultList.as_view(), name='api-result-list'),
    path('api/v1/execution/<int:id>/result/<int:last_id>', views.ResultListFiltered.as_view(), name='api-result-list-filtered'),
    
    path('api/v1/apparatus', views.ApparatusListAPI.as_view(), name='api-apparatus-list'),
    path('api/v1/apparatus/<int:id>/heartbeat', views.Heartbeat.as_view(), name='api-apparatus-heartbeat'),
    path('api/v1/apparatus/<int:id>', views.ApparatusView.as_view(), name='api-apparatus-view'),
    path('api/v1/apparatus/<int:id>/nextexecution', views.NextExecution.as_view(), name='api-execution-next'),
    path('api/v1/apparatus/<int:id>/queue', views.ExecutionQueue.as_view(), name='api-execution-queue'),

    path('api/v1/result', views.AddResult.as_view(), name='api-result-add'),
]