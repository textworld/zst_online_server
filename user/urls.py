from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

urlpatterns = [
    path('login/', views.LoginAPIView.as_view(), name='login'),
    # path('register/', views.django_register),
    # path('is_login/', views.django_is_login)
]
