from django.urls import path, include
from rest_framework.routers import DefaultRouter
from schema_info.views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'mysql_schema', SchemaViewSet, basename='mysql_schema')


urlpatterns = [
    *router.urls,
    path('query_result/', query_result),
    path('install_mysql/', install_mysql)
]
