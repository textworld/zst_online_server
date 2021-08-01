from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'schema_view', SchemaViewSet, basename='db_schema')
router.register(r'instance_view', InstanceViewSet, basename='db_instance')
router.register(r'ansible_task', AnsibleResultViews, basename='ansible_result')
router.register(r'es_document', SlowSQLViewSet, basename='es_document')
router.register(r'alarm_setting', AlarmSettingViewSet, basename='alarm_setting')

urlpatterns = [
    *router.urls,
    path('send_mail/', send_email_simple),
    path('send_html_email/', send_html_email),
    path('send_email_with_pic/', send_email_with_pic),
    path('send_with_matplotlib/', send_with_matplotlib),
    path('test/', alarm_minute)
]
