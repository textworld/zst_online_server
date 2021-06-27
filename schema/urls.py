from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'schema_view', SchemaViewSet, basename='mysql_schema')

urlpatterns = [
    *router.urls
]