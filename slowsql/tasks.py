from celery import shared_task
from alarm.alarm import WexinAlarm
from slowsql.helper import get_aggs, get_results
from slowsql.models import AlarmSettingModel
from slowsql.esmodel import SlowQuery
import redis
from django.conf import settings
import time

msg_sender = WexinAlarm()


def send_slow_alarm(record):
    # TODO： 加上告警记录
    msg_template = "您的数据库【{}】存在慢SQL: {}，平均执行时间为{}，一分钟执行了{}次，请关注"
    s = SlowQuery.search()
    results = s.filter("term", hash__keyword=record['hash']).execute()
    print(results)
    sql_printer = ""
    if len(results.hits.hits) > 0:
        sql_printer = results.hits.hits[0]['_source']['finger']
    msg = msg_template.format(record['schema'], sql_printer, record['avg_query_time'], record['hash_count'])
    msg_sender.send_msg("ZhangWenBing", msg)

@shared_task
def alarm_minute():
    # 从settings中获取配置信息
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    key_name = "slowsql_alarm_start"
    duration = 60
    start = int(time.time()) - duration

    if r.exists(key_name):
        start = r.get(key_name)
    else:
        r.set(key_name, start + duration)
    end = start + duration

    print("start: {}, type: {}".format(start, type(start)))

    global_query_time = 10
    global_query_count = 10

    global_cfg = AlarmSettingModel.objects.filter(schema=None).order_by("-id")
    if global_cfg.exists():
        global_query_time = global_cfg.first().query_time
        global_query_count = global_cfg.first().query_count

    s = SlowQuery.search()

    options = {
        # greater or equal than  -> gte 大于等于
        # greater than  -> gt 大于
        # little or equal thant -> lte 小于或等于
        'gte': start,
        'lte': end
    }
    s = s.filter('range', **{'@timestamp': options})
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