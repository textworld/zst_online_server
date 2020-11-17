from rest_framework.views import APIView
from rest_framework.response import Response

from django.contrib.auth import login, logout, authenticate
from django.http.response import HttpResponseNotAllowed, HttpResponse
from django.contrib.auth import get_user_model
from .serializers import LoginSerializer, UserSerializer
from rest_framework import exceptions
from django.utils.translation import gettext as _


class LoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(True)
        user = authenticate(request, **serializer.validated_data)
        if user is None:
            raise exceptions.ValidationError(_("invalid username or password"))
        login(request, user)
        return Response(UserSerializer(user).data)

#
# def django_login(request):
#     username = request.POST['username']
#     password = request.POST['password']
#     user = authenticate(request, username=username, password=password)
#     if user is None:
#         return HttpResponse('error username or password', status=401)
#     login(request, user)
#     return HttpResponse('login success')
#
# def django_true_login(request):
#     username = request.POST['username']
#     password = request.POST['password']
#     login()
#
# def django_is_login(request):
#     print(request.user) # 如果没有登录的话，那么输出AnonymousUser
#     # 还有其他的一些有用的属性
#     # request.user.is_superuser
#     request.user.is_authenticated
#     if request.user.is_authenticated:
#         return HttpResponse('is logined')
#     return HttpResponse('not login', status=401)
#
# def django_register(request):
#     email = request.POST['email']
#     username = request.POST['username']
#     password = request.POST['password']
#     User = get_user_model()
#     field_meta = User._meta.get_field('username')
#     max_length = field_meta.max_length
#
#     user = User()
#     setattr(user, 'username', username)
#     setattr(user, 'email', email)
#     user.set_password(password)
#     user.save()
#     return HttpResponse('register success')

