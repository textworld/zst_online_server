from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import MenuAPIView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'menu', MenuAPIView, basename='menu')


urlpatterns = [
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('user_info/', views.UserDetail.as_view(), name='current_user'),
    *router.urls
    # path('register/', views.django_register),
    # path('is_login/', views.django_is_login)
]
