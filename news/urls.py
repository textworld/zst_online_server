from django.urls import path, include
from rest_framework.routers import DefaultRouter
from news.views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'news', NewsViewSet, basename='news')

urlpatterns = [
    *router.urls,
    path('test/', test),
    path('scrap/', scraper)
]
