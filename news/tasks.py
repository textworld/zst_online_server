from celery import shared_task, Task
import requests
import json
from .models import ProxyModel

@shared_task
def periodic_check_mysql():
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


@shared_task
def scrap_news():
    pass