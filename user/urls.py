from django.urls import path, include
from .views import *

urlpatterns = [
    path('login/', LoginAPIView.as_view()),
    path('user/', UserDetail.as_view()),
    path('logout/', user_logout)
]
