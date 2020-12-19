from slowsql.views import SlowSqlViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'query', SlowSqlViewSet, basename='slowsql_query')
urlpatterns = router.urls
