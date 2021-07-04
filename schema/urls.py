from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'schema_view', SchemaViewSet, basename='db_schema')
router.register(r'instance_view', InstanceViewSet, basename='db_instance')
router.register(r'ansible_task', AnsibleResultViews, basename='ansible_result')

urlpatterns = [
    *router.urls,
    path('add_request/', add_request)
]