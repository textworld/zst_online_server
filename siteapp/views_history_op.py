import requests
from django.http.response import HttpResponse
import json
from .models import ProxyModel, NewsModel
from bs4 import BeautifulSoup
import datetime
import hashlib
from rest_framework import status, viewsets
from .serializer import HistoryOpSerializer
from rest_framework.pagination import PageNumberPagination

from siteapp.models import HistoryOpModel
from django.utils.decorators import method_decorator


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = 'page_num'
    max_page_size = 500


# 操作历史
class HistoryOpViewSet(viewsets.ModelViewSet):
    queryset = HistoryOpModel.objects.all()
    serializer_class = HistoryOpSerializer
    pagination_class = CustomPagination
