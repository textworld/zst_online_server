from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict
from djoser import serializers as djoser_serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import collections
from rest_framework.status import HTTP_200_OK
from .models import Role, Permission, ActionSet
from . import models

User = get_user_model()

class WrapMixins:
    @property
    def data(self):
        ret = super().data
        json = {
            'code': 200,
            'message': 'good',
            'result': ret
        }
        return ReturnDict(json, serializer=self)

    @classmethod
    def many_init(cls, *args, **kwargs):
        kwargs['child'] = cls()
        return ZstListSerializers(*args, **kwargs)
#
#
# class SimplePermissionSerializers(serializers.ModelSerializer):
#     class Meta:
#         model = Permission
#         fields = '__all__'
#
#
# class SimpleContentTypeSerializers(WrapMixins, serializers.ModelSerializer):
#     permissions = serializers.SerializerMethodField()
#
#     class Meta:
#         model = ContentType
#         fields = '__all__'
#
#     def get_permissions(self, obj):
#         print(obj)
#         permission_serializer = SimplePermissionSerializers(obj.permission_set.all(), many=True)
#         return permission_serializer.data
#
#
#
# class ContentTypeSerializers(serializers.ModelSerializer):
#     class Meta:
#         model = ContentType
#         fields = '__all__'
#
#
# class PermissionSerializers(serializers.ModelSerializer):
#     content_type = ContentTypeSerializers(read_only=True)
#
#     class Meta:
#         model = Permission
#         fields = '__all__'
#
#
# class GroupSerializers(WrapMixins, serializers.ModelSerializer):
#     permissions = PermissionSerializers(many=True, read_only=True)
#
#     class Meta:
#         model = Group
#         fields = '__all__'


class ZstUserSerializers(djoser_serializers.UserSerializer):

    @property
    def data(self):
        ret = super().data
        json = {
            'code': 200,
            'message': 'good',
            'result': ret
        }
        return ReturnDict(json, serializer=self)

    @classmethod
    def many_init(cls, *args, **kwargs):
        kwargs['child'] = cls()
        return ZstListSerializers(*args, **kwargs)


class ZstListSerializers(serializers.ListSerializer):
    def update(self, instance, validated_data):
        pass

    @property
    def data(self):
        ret = super().data
        json = {
            'code': 200,
            'message': 'good',
            'result': ret
        }
        return ReturnDict(json, serializer=self)


class ZstTokenRefreshSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        json = {
            'code': HTTP_200_OK,
            'message': 'good',
            'result': data
        }
        return json


class ZstPermissionSerializer(WrapMixins, serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class ZstRoleSerializer(WrapMixins, serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class ZstActionSerializer(WrapMixins, serializers.ModelSerializer):
    class Meta:
        model = ActionSet
        fields = '__all__'


class GrantUserRoleSerializer(serializers.Serializer):
    role_list = serializers.ListField(child=serializers.IntegerField(min_value=0), allow_empty=True, write_only=True)

    def update(self, instance, validated_data):
        user = models.ZstUser.objects.get(pk=validated_data['uid'])
        roles = models.Role.objects.filter(pk__in=validated_data['role_list'])
        user.roles.clear()
        if roles.count > 0:
            user.roles.add(*roles)
        return user

    def create(self, validated_data):
        user = models.ZstUser.objects.get(pk=validated_data['uid'])
        roles = models.Role.objects.filter(pk__in=validated_data['role_list'])
        user.roles.add(*roles)
        return user

    def validate_role_list(self, value):
        if len(value) == 0:
            return value

        value = list(set(value))
        roles = models.Role.objects.filter(id__in=value)
        if roles.count() < len(value):
            raise serializers.ValidationError("invalid list of role id")

        return value


