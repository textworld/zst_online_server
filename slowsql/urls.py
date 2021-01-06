from slowsql.views import SlowSqlViewSet, AlarmSettingViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'query', SlowSqlViewSet, basename='slowsql_query')
router.register(r'setting', AlarmSettingViewSet, basename='setting')
urlpatterns = router.urls
