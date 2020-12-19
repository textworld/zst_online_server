from slowsql.views import UserViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'query', UserViewSet, basename='slowsql_query')
urlpatterns = router.urls