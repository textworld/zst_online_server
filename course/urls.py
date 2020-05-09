from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from .views import CourseViewSet


router = routers.DefaultRouter()
router.register(r'course', CourseViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
#yxh test
#yxh test2
# yexihui test4