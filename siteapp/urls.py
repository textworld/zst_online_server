from django.urls import path, include
from rest_framework.routers import DefaultRouter
from siteapp.views import *
from siteapp.views_history_op import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'news', NewsViewSet, basename='news')
router.register(r'history_op', HistoryOpViewSet, basename='history_op')

urlpatterns = [
    *router.urls,
    path('test/', test),
    path('scrap/', scraper)
]
