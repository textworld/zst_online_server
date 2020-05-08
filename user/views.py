from . import serializers, models
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import Group, Permission, ContentType


class ZstTokenObtainPairView(TokenObtainPairView):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    serializer_class = serializers.ZstTokenRefreshSerializer


# class GroupViewSet(viewsets.ModelViewSet):
#     serializer_class = serializers.GroupSerializers
#     queryset = Group.objects.all()
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         permissions = Permission.objects.filter(id__in=request.data['permissions'])
#         serializer.instance.permissions.add(*permissions)
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
#
#     def update(self, request, *args, **kwargs):
#         try:
#             group = Group.objects.get(id=int(kwargs['pk']))
#         except Group.DoesNotExist:
#             return Response({"message": "not found", "code": 404, "result": ""}, status=status.HTTP_404_NOT_FOUND)
#
#         permissions = Permission.objects.filter(id__in=request.data['permissions'])
#         group.permissions.clear()
#         group.permissions.add(*permissions)
#         return Response({"message": "success", "code": 200, "result": ""}, status=status.HTTP_202_ACCEPTED)


class ContentTypeList(APIView):
    def get(self, request):
        rows = ContentType.objects.all()
        serializer = serializers.SimpleContentTypeSerializers(rows, many=True)
        return Response(serializer.data)


class ZstRoleViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ZstRoleSerializer
    queryset = models.Role.objects.all()


class ZstPermissionViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ZstPermissionSerializer
    queryset = models.Permission.objects.all()


class ZstActionSetViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ZstActionSerializer
    queryset = models.ActionSet.objects.all()


class ZstUserSetViewSet(viewsets.ModelViewSet):
    queryset = models.ZstUser.objects.all()
    serializer_class = serializers.ZstUserSerializers

    @action(detail=True, methods=['post'])
    def grantRoles(self, request, pk=None):
        print(pk)
        serializer = serializers.GrantUserRoleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'code': status.HTTP_400_BAD_REQUEST, 'message': 'invalid', 'result': serializer.errors})

        u = serializer.save(uid=int(pk))

        return Response({'code': status.HTTP_200_OK, 'message': 'success', 'result': u.roles.all().values_list('id', flat=True)})