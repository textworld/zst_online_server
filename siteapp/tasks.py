from celery import shared_task, Task
import requests
import json
from news.models import ProxyModel, NewsModel
from bs4 import BeautifulSoup
import datetime
import hashlib
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

@shared_task
def periodic_fetch_proxy_from_zhima():
    url = "http://webapi.http.zhimacangku.com/getip?num=1&type=2&pro=&city=0&yys=0&port=1&pack=131583&ts=1&ys=1&cs=1&lb=3&sb=0&pb=4&mr=1&regions="
    resp = requests.get(url)
    try:
        if resp.status_code >= 300:
            raise Exception("incorrect status_code {}:{}".format(resp.status_code, resp.text))

        body = json.loads(resp.text)
        if body['code'] != 0:
            raise Exception("incorrect code in resp: {}", resp.text)

        data = body['data'][0]
        try:
            m = ProxyModel.objects.get(ip=data['ip'], port=data['port'])
            m.expire_time = data['expire_time']
            m.city = data['city']
            m.isp = data['isp']
        except ProxyModel.DoesNotExist:
            m = ProxyModel(**data)
        m.save()
    except Exception as e:
        logger.error("failed to get proxy server from zhima: {}".format(e))


@shared_task
def scrap_news():
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context

    proxies = ProxyModel.objects.filter(expire_time__gt=datetime.datetime.now()).order_by('-failed_count')
    if not proxies.exists():
        return "no proxy found"

    proxy_ip = proxies[0]
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
            return "success"
        else:
            return "failed"
    except requests.exceptions.RequestException as e:
        proxy_ip.call_count += 1
        proxy_ip.failed_count += 1

    finally:
        proxy_ip.save()

    return "failed"