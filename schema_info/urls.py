from django.urls import path, include
from rest_framework.routers import DefaultRouter
from schema_info.views import SchemaViewSet
from rest_framework.routers import DefaultRouter
from schema_info.views import login_test, add_request, query_task_result, group_request

router = DefaultRouter()
router.register(r'mysql_schema', SchemaViewSet, basename='mysql_schema')


urlpatterns = [
    *router.urls,
    path('user/djlogin/loginAPI/', login_test),
    path('add/', add_request),
    path('result/', query_task_result),
    path('group_request/', group_request)
]
