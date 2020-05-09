from rest_framework import viewsets
from .serializers import CourseSerializer
from .models import Course
from user.permission import ZstAccessPolicy
from django.contrib.auth import get_user_model

User = get_user_model()


class CourseViewSet(viewsets.ModelViewSet):
    permission_name = "course"
    permission_classes = (ZstAccessPolicy,)
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
