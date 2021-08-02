from django.contrib.auth import login, authenticate, logout
from django.utils.translation import gettext as _
from rest_framework import exceptions
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from .serializers import LoginSerializer, UserSerializer


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(True)
        user = authenticate(request, **serializer.validated_data)
        if user is None:
            raise exceptions.ValidationError(_("invalid username or password"))
        login(request, user)
        return Response(UserSerializer(user).data)


class UserDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        return Response(UserSerializer(user).data)


@api_view()
def user_logout(request):
    logout(request)
    return Response()
