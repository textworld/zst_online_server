from django.shortcuts import render
from rest_framework import viewsets
from .serializers import CourseSerializer
from .models import Course
from django.contrib.contenttypes.models import ContentType
from rest_access_policy import AccessPolicy


class UserAccessPolicy(AccessPolicy):
    # ... other properties and methods ...

    def get_user_group_values(self, user):
        return list(user.roles.values_list("title", flat=True))


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()