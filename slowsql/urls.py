from slowsql.views import SlowSqlViewSet, AlarmSettingViewSet, save_global_setting
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register(r'query', SlowSqlViewSet, basename='slowsql_query')
router.register(r'setting', AlarmSettingViewSet, basename='setting')

urlpatterns = [
    *router.urls,
    path('global_setting/', save_global_setting),
]
