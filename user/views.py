from . import serializers, models
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import Group, Permission, ContentType

from django.contrib.auth import login, logout, authenticate
from django.http.response import HttpResponseNotAllowed, HttpResponse

def django_login(request):
    username = request.POST['username']
    password = request.POST['password']
    if not authenticate(username, password):
        return HttpResponse('error username or password', status_code=401)
    return HttpResponse('login success')

def django_register(request):
    username = request.POST['username']
    password = request.POST['password']

