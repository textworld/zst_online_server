from django.shortcuts import render
import requests
from django.http.response import HttpResponse
import json
from .models import ProxyModel, NewsModel
from bs4 import BeautifulSoup
import datetime
import hashlib
from rest_framework import status, viewsets
from .serializer import NewsSerializer
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = 'page_num'
    max_page_size = 500


class NewsViewSet(viewsets.ModelViewSet):
    queryset = NewsModel.objects.order_by('-insert_time').all()
    serializer_class = NewsSerializer
    pagination_class = CustomPagination


# Create your views here.
def test(request):
    url = "http://webapi.http.zhimacangku.com/getip?num=1&type=2&pro=&city=0&yys=0&port=1&pack=131583&ts=1&ys=1&cs=1&lb=3&sb=0&pb=4&mr=1&regions="
    resp = requests.get(url)
    if resp.status_code == 200:
        body = json.loads(resp.text)
        if body['code'] == 0:
            data = body['data'][0]
            try:
                m = ProxyModel.objects.get(ip=data['ip'], port=data['port'])
                m.expire_time = data['expire_time']
                m.city = data['city']
                m.isp = data['isp']
            except ProxyModel.DoesNotExist:
                m = ProxyModel(**data)
            m.save()
    return HttpResponse({"data": "success"})


def scraper(request):
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context

    proxies = ProxyModel.objects.filter(expire_time__gt=datetime.datetime.now()).order_by('-failed_count')
    if not proxies.exists():
        return HttpResponse("no proxy found")
    proxy_ip =proxies[0]
    proxyMeta = "http://%(host)s:%(port)s" % {

        "host": proxy_ip.ip,
        "port": str(proxy_ip.port),
    }
    proxies = {
        "http": proxyMeta,
        "https": proxyMeta
    }

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/51.0.2704.63 Safari/537.36'}
    try:
        resp = requests.get("https://dbaplus.cn/", headers=headers, proxies=proxies, timeout=5)
        proxy_ip.call_count += 1
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            for h3 in soup.find(id='tabAll').find_all(class_='media-heading'):
                title = h3.a.get_text()
                href = h3.a['href']
                hash = hashlib.md5(href.encode('utf-8')).hexdigest()
                try:
                    n = NewsModel.objects.get(hash=hash)
                    n.title = title
                except NewsModel.DoesNotExist:
                    n = NewsModel(title=title, url=href, hash=hash)

                n.save()
            return HttpResponse("success")
        else:
            return HttpResponse("failed")
    except requests.exceptions.RequestException as e:
        proxy_ip.call_count += 1
        proxy_ip.failed_count += 1

    finally:
        proxy_ip.save()

    return HttpResponse("failed")

