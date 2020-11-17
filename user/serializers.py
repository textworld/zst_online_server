from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict
import collections
from rest_framework.status import HTTP_200_OK
from .models import Role, Permission, ActionSet
from . import models


class LoginSerializer(serializers.Serializer):
    username = serializers.SlugField(required=True, help_text="用户名", max_length=64)
    password = serializers.CharField(required=True, help_text="密码",  write_only=True, max_length=64, min_length=6)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["username", "email"]