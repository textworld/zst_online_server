from django.shortcuts import render

from elasticsearch_dsl import Q, A
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from slowsql.esmodel import SlowQuery
from rest_framework.decorators import action
from slowsql.models import AlarmSettingModel
from slowsql.serializer import AlarmSettingSerializer, AddGlbAlarmSerializer
from django.http.response import HttpResponse
from datetime import datetime
import time
import requests
import json
from email.mime.text import MIMEText
from email.utils import formataddr
from django.template.loader import render_to_string
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
import matplotlib
from pylab import mpl
import os
from .helper import get_aggs,get_results,build_aggs

token = ""
expire = int(time.time())


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = 'page_num'
    max_page_size = 500


def send_email_simple(request):
    import smtplib
    my_sender = "zhangwenbing@zstpython.onexmail.com"
    # 邮件的内容
    msg = MIMEText('这是一条测试邮件,请忽略', 'plain', 'utf-8')
    # [发件人的邮箱昵称、发件人邮箱账号], 昵称随便
    msg['From'] = formataddr([" ", my_sender])
    # [收件人邮箱昵称、收件人邮箱账号], 昵称随便
    msg['To'] = formataddr([" ", "text.zwb@outlook.com"])
    # 邮件的主题，也就是邮件的标题
    msg['Subject'] = "邮件测试"

    server = smtplib.SMTP_SSL('smtp.exmail.qq.com', 465)

    # server.starttls()
    # Next, log in to the server
    server.login(my_sender, "ZSTmail2021")

    server.sendmail("zhangwenbing@zstpython.onexmail.com", "text.zwb@outlook.com", msg.as_string())
    server.quit()
    return HttpResponse("success")


def send_html_email(request):
    report = render_to_string("slowsql.html", context={
        "send_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    my_sender = "zhangwenbing@zstpython.onexmail.com"
    # 邮件的内容
    msg = MIMEText(report, 'html', 'utf-8')
    # [发件人的邮箱昵称、发件人邮箱账号], 昵称随便
    msg['From'] = formataddr([" ", my_sender])
    # [收件人邮箱昵称、收件人邮箱账号], 昵称随便
    msg['To'] = formataddr([" ", "text.zwb@outlook.com"])
    # 邮件的主题，也就是邮件的标题
    msg['Subject'] = "慢SQL周报"

    server = smtplib.SMTP_SSL('smtp.exmail.qq.com', 465)

    # server.starttls()
    # Next, log in to the server
    server.login(my_sender, "ZSTmail2021")

    server.sendmail("zhangwenbing@zstpython.onexmail.com", "text.zwb@outlook.com", msg.as_string())
    server.quit()

    return HttpResponse("success")


def send_email_with_pic(request):
    report = render_to_string("slowsql.html", context={
        "send_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    my_sender = "zhangwenbing@zstpython.onexmail.com"

    msg = MIMEMultipart('related')
    msg['From'] = formataddr([" ", my_sender])
    # [收件人邮箱昵称、收件人邮箱账号], 昵称随便
    msg['To'] = formataddr([" ", "text.zwb@outlook.com"])
    # 邮件的主题，也就是邮件的标题
    msg['Subject'] = "慢SQL周报"
    msg.attach(MIMEText(report, 'html', 'utf-8'))

    with open("./slowsql/kubernetes.png", "rb") as f:
        pic = MIMEImage(f.read())
        pic.add_header('Content-ID', '<pic>')
        msg.attach(pic)

    server = smtplib.SMTP_SSL('smtp.exmail.qq.com', 465)

    # server.starttls()
    # Next, log in to the server
    server.login(my_sender, "ZSTmail2021")

    server.sendmail("zhangwenbing@zstpython.onexmail.com", "text.zwb@outlook.com", msg.as_string())
    server.quit()

    return HttpResponse("success")


def send_with_matplotlib(request):

    s = SlowQuery.search()
    options = {
        # greater or equal than  -> gte 大于等于
        # greater than  -> gt 大于
        # little or equal thant -> lte 小于或等于
        'gte': '2019-12-01T00:00:00.000Z',
        'lte': '2019-12-31T00:00:00.000Z'
    }
    s = s.filter('range', **{'@timestamp': options})
    aggs = {
        "aggs": {
            "date": {
                "date_histogram": {
                    "field": "@timestamp",
                    "calendar_interval": "day"
                },
                "aggs": {
                    "avg_query_time": {
                        "avg": {
                            "field": "query_time"
                        }
                    },
                    "avg_lock_time": {
                        "avg": {
                            "field": "lock_time"
                        }
                    }
                }
            }
        }
    }
    get_aggs(s.aggs, aggs)
    result = s.execute().aggregations
    rs = get_results(aggs, result)
    dates = [r['date'][:10] for r in rs]
    counts = [r['date_count'] for r in rs]

    rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    matplotlib.rcParams['font.family'] = 'SimHei'
    mpl.rcParams['font.sans-serif'] = ['SimHei']  # 更新字体格式
    mpl.rcParams['font.size'] = 14

    plt.figure(figsize=(12, 4))
    # 生成图形
    plt.title('慢SQL数量趋势图')
    plt.plot(dates, np.asarray(counts), label='慢SQL数量')
    plt.legend()

    plt.xticks(rotation=-30, ha='left')
    plt.tick_params(axis='x', labelsize=8)
    # 显示图形
    now = float(time.time())
    pic_name = str(now) + ".jpg"
    plt.savefig(pic_name)
    plt.close()

    report = render_to_string("slowsql.html", context={
        "send_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    my_sender = "zhangwenbing@zstpython.onexmail.com"

    msg = MIMEMultipart('related')
    msg['From'] = formataddr([" ", my_sender])
    # [收件人邮箱昵称、收件人邮箱账号], 昵称随便
    msg['To'] = formataddr([" ", "text.zwb@outlook.com"])
    # 邮件的主题，也就是邮件的标题
    msg['Subject'] = "慢SQL周报"
    msg.attach(MIMEText(report, 'html', 'utf-8'))

    with open(pic_name, "rb") as f:
        pic = MIMEImage(f.read())
        pic.add_header('Content-ID', '<pic>')
        msg.attach(pic)

    server = smtplib.SMTP_SSL('smtp.exmail.qq.com', 465)

    # server.starttls()
    # Next, log in to the server
    server.login(my_sender, "ZSTmail2021")

    server.sendmail("zhangwenbing@zstpython.onexmail.com", "text.zwb@outlook.com", msg.as_string())
    server.quit()

    os.remove(pic_name)
    return HttpResponse("success")

def get_token():
    global token, expire
    now = int(time.time())
    if now < expire and len(token) > 0:
        return token

    url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=ww2ef294fd1f043429&corpsecret=deLb5gd4hiP-l5ekwbEZ6h1WZbGz43VPOWgqwRrfqIM"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code > 300:
        raise Exception("无法获取token:" + response.text)

    resp_obj = json.loads(response.text)
    if resp_obj['errcode'] != 0:
        raise Exception("无法获取token:" + resp_obj['errmsg'])

    token = resp_obj['access_token']
    expire = int(time.time()) + resp_obj['expires_in']
    return token


def send_wechat_msg(user, message):
    access_token = get_token()

    url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + access_token

    payload = {
        "touser": user,
        "toparty": "1",
        "msgtype": "text",
        "agentid": 1000002,
        "text": {
            "content": message
        },
        "safe": 0,
        "enable_id_trans": 0,
        "enable_duplicate_check": 0,
        "duplicate_check_interval": 1800
    }
    headers = {
        'Content-Type': 'application/json'
    }

    resp = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    print(resp.status_code)
    print(resp.text)


def send_slow_alarm(record):
    msg_template = "您的数据库【{}】存在慢SQL: {}，平均执行时间为{}，一分钟执行了{}次，请关注"
    s = SlowQuery.search()
    results = s.filter("term", hash__keyword=record['hash']).execute()
    print(results)
    sql_printer = ""
    if len(results.hits.hits) > 0:
        sql_printer = results.hits.hits[0]['_source']['finger']
    msg = msg_template.format(record['schema'], sql_printer, record['avg_query_time'], record['hash_count'])
    send_wechat_msg("ZhangWenBing", msg)


def alarm(request):
    end = int(time.time())
    start = end - 60

    global_query_time = 10
    global_query_count = 10

    global_cfg = AlarmSettingModel.objects.filter(schema=None).order_by("-id")
    if global_cfg.exists():
        global_query_time = global_cfg.first().query_time
        global_query_count = global_cfg.first().query_count

    s = SlowQuery.search()

    # options = {
    #     # greater or equal than  -> gte 大于等于
    #     # greater than  -> gt 大于
    #     # little or equal thant -> lte 小于或等于
    #     'gte': start,
    #     'lte': end
    # }
    # s = s.filter('range', **{'@timestamp': options})
    aggs = {
        "aggs": {
            "schema": {
                "terms": {
                    "field": "schema.keyword"
                },
                "aggs": {
                    "hash": {
                        "terms": {
                            "field": "hash.keyword"
                        },
                        "aggs": {
                            "avg_query_time": {
                                "avg": {
                                    "field": "query_time"
                                }
                            },
                            "avg_lock_time": {
                                "avg": {
                                    "field": "lock_time"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    get_aggs(s.aggs, aggs)

    result = s.execute().aggregations

    rs = get_results(aggs, result)

    schema_cfg_dict = {}
    schema_cfg_queryset = AlarmSettingModel.objects.exclude(schema__isnull=True).filter(stop_alarm=False, delete=False)
    for schema_cfg in schema_cfg_queryset:
        # schema_cfg_dict[schema_cfg.schema + "#" + schema_cfg.sql_print_hash] = schema_cfg
        cfg_key = schema_cfg.schema.schema + "#" + schema_cfg.sql_print_hash
        schema_cfg_dict[cfg_key] = schema_cfg

    for r in rs:
        threshold_query_time = global_query_time
        threshold_query_count = global_query_count
        cfg = schema_cfg_dict.get(r.get('schema') + "#" + r.get('hash'), None)
        if cfg is not None:
            threshold_query_count = cfg.query_count
            threshold_query_time = cfg.query_time
        if r['avg_query_time'] > threshold_query_time and r['hash_count'] > threshold_query_count:
            send_slow_alarm(r)
            break

    return HttpResponse("success")


class AlarmSettingViewSet(viewsets.ModelViewSet):
    queryset = AlarmSettingModel.objects.exclude(schema__isnull=True)
    serializer_class = AlarmSettingSerializer

    @action(detail=False, methods=['post', 'get'])
    def global_setting(self, request, *args, **kwargs):
        if request.method == 'POST':
            s = AddGlbAlarmSerializer(data=request.data)
            s.is_valid(raise_exception=True)
            instance = s.save()
            return Response("success")

        settings = AlarmSettingModel.objects.filter(schema=None).order_by("-id")
        if not settings.exists():
            return Response([])

        return Response(AddGlbAlarmSerializer(settings.first()).data)


class SlowSqlViewSet(viewsets.ViewSet):
    def get_int_params(self, request, name, default_val):
        val = request.query_params.get(name, None)

        if val is not None and isinstance(val, str) and val.isnumeric():
            val = int(val)
        else:
            val = default_val
        return val

    @action(detail=False, methods=['get'])
    def get_aggs_by_date(self, request, *args, **kwargs):
        s = self.get_query_by_params(request, sorts="@timestamp")
        aggs = {
            "aggs": {
                "date": {
                    "date_histogram": {
                        "field": "@timestamp",
                        "calendar_interval": 'day'
                    }
                }
            }
        }
        get_aggs(s.aggs, aggs)

        result = s.execute().aggregations

        rs = get_results(aggs, result)
        return Response(rs)

    @action(detail=False, methods=['get'])
    def get_top10_sql(self, request, *args, **kwargs):
        s = self.get_query_by_params(request)
        composite = A('terms', script="doc['schema.keyword'].value+'#'+doc['hash.keyword'].value", size=10)
        s.aggs.bucket('sql', composite).bucket('finger', A('top_hits', _source=["finger"], size=1))
        aggs = s.execute().aggregations
        results = []
        for bucket in aggs.sql.buckets:
            k = bucket.key
            keys = k.split('#')
            data = {
                "schema": keys[0],
                "hash": keys[1],
                "count": bucket.doc_count,
                "finger": bucket.finger.hits.hits[0]['_source']['finger']
            }
            results.append(data)

        return Response(results)

    @action(detail=False, methods=['get'])
    def get_aggs_by_schema(self, request, *args, **kwargs):
        s = self.get_query_by_params(request)
        aggs = {
            "aggs":
                {
                    "schema": {
                        "terms": {
                            "field": "schema.keyword"
                        }
                    }
                }
        }
        get_aggs(s.aggs, aggs)

        result = s.execute().aggregations

        rs = get_results(aggs, result)
        return Response(rs)

    # 通用获取参数
    def get_query_by_params(self, request, sorts=None):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        s = SlowQuery.search()
        if start is None or not isinstance(start, str) or len(start.strip()) == 0:
            start = None
        if end is None or not isinstance(end, str) or len(end.strip()) == 0:
            end = None

        if start is not None and end is not None:
            options = {
                # greater or equal than  -> gte 大于等于
                # greater than  -> gt 大于
                # little or equal thant -> lte 小于或等于
                'gte': start,
                'lte': end
            }
            s = s.filter('range', **{'@timestamp': options})

        sorts = request.query_params.get('sorts', sorts)
        if isinstance(sorts, str) and len(sorts) > 0:
            sorts = [item.strip() for item in sorts.split(",") if len(item.strip()) > 0]
            s = s.sort(*sorts)
        else:
            s = s.sort('-@timestamp')
        return s

    def list(self, request, *args, **kwargs):
        # 入参： 开始时间、结束时间、库名、第几页、每页多少个
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        schema = request.query_params.get('schema', None)
        is_aggr_by_hash = request.query_params.get('is_aggr_by_hash', False)
        if isinstance(is_aggr_by_hash, str) and is_aggr_by_hash.lower() == 'true':
            is_aggr_by_hash = True
        else:
            is_aggr_by_hash = False

        interval = request.query_params.get('interval', '1d')

        # 参数验证过程就省略
        s = SlowQuery.search()
        if schema is not None and len(schema) > 0:
            s = s.filter('term', schema__keyword=schema)
        if start is not None and end is not None:
            options = {
                # greater or equal than  -> gte 大于等于
                # greater than  -> gt 大于
                # little or equal thant -> lte 小于或等于
                'gte': start,
                'lte': end
            }
            s = s.filter('range', **{'@timestamp': options})

        s = s.sort('-@timestamp')
        paginator = CustomPagination()

        if is_aggr_by_hash:
            aggs = {
                "aggs": {
                    "date": {
                        "date_histogram": {
                            "field": "@timestamp",
                            "calendar_interval": interval
                        },
                        "aggs": {
                            "schema": {
                                "terms": {
                                    "field": "schema.keyword"
                                },
                                "aggs": {
                                    "hash": {
                                        "terms": {
                                            "field": "hash.keyword"
                                        },
                                        "aggs": {
                                            "rows_sent": {
                                                "avg": {
                                                    "field": "rows_sent"
                                                }
                                            },
                                            "rows_examined": {
                                                "avg": {
                                                    "field": "rows_examined"
                                                }
                                            },
                                            "query_time": {
                                                "avg": {
                                                    "field": "query_time"
                                                }
                                            },
                                            "sql": {
                                                "top_hits": {
                                                    "_source": [
                                                        "finger",
                                                        "@timestamp"
                                                    ],
                                                    "sort": [
                                                        {
                                                            "@timestamp": {
                                                                "order": "desc"
                                                            }
                                                        }
                                                    ],
                                                    "size": 1
                                                }
                                            }

                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            get_aggs(s.aggs, aggs)

            result = s.execute().aggregations

            rs = get_results(aggs, result)
        if is_aggr_by_hash:
            data = paginator.paginate_queryset(rs, request)
        else:
            data = paginator.paginate_queryset(s, request)
            data = [q.to_dict() for q in data]

        # 补充处理
        return paginator.get_paginated_response(data)
