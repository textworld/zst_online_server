from .views import ZstTokenObtainPairView, ContentTypeList
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register('permission', views.ZstPermissionViewSet)
router.register('role', views.ZstRoleViewSet)
router.register('actionset', views.ZstActionSetViewSet)
router.register('zstuser', views.ZstUserSetViewSet)

urlpatterns = [
    path('jwt/create/', ZstTokenObtainPairView.as_view()),
    path('content-type/', ContentTypeList.as_view()),
    path('', include(router.urls)),
]
