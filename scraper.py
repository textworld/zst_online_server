import requests
import ssl
from bs4 import BeautifulSoup
ssl._create_default_https_context = ssl._create_unverified_context

import jinja2

if __name__ == '__main__':
    jinja2.
    # http://h.zhimaruanjian.com/ucenter/?first_time=1#info
    import requests

    # 请求地址
    targetUrl = "https://www.baidu.com"

    # 代理服务器
    proxyHost = "175.23.240.107"
    proxyPort = "4278"

    proxyMeta = "http://%(host)s:%(port)s" % {

        "host": proxyHost,
        "port": proxyPort,
    }

    proxies = {

        "http": proxyMeta,
        "https": proxyMeta
    }

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/51.0.2704.63 Safari/537.36'}
    resp = requests.get("https://dbaplus.cn/", headers=headers, proxies=proxies)
    if resp.status_code == 200:
        print(resp.text)
        soup = BeautifulSoup(resp.text, 'html.parser')
        for h3 in soup.find(id='tabAll').find_all(class_='media-heading'):
            print(h3.a.get_text())
            print(h3.a['href'])
    else:
        print("failed")