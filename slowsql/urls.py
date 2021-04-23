from slowsql.views import SlowSqlViewSet, AlarmSettingViewSet, alarm, send_email_simple, send_html_email, send_email_with_pic
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from slowsql.views import send_with_matplotlib

router = DefaultRouter()
router.register(r'query', SlowSqlViewSet, basename='slowsql_query')
router.register(r'setting', AlarmSettingViewSet, basename='setting')

urlpatterns = [
    *router.urls,
    path('alarm/', alarm),
    path('send_email/', send_email_simple),
    path('send_email_html/', send_html_email),
    path('send_email_html_pic/', send_email_with_pic),
    path('send_with_matplotlib/', send_with_matplotlib)
]
