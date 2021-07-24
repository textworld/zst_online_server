# pip install kafka-python
import requests
from elasticsearch import Elasticsearch
from kafka import KafkaConsumer
import json
import random
import time
import logging
import sys

from functools import wraps


# fail_retry(try_times) 相当于 decorator
# decorator(func) 相当于 wrapper
# wrapper(a) 相当于fun(a)
# @fail_retry(try_times) 相当于 func = fail_retry(try_times)(func)
# 所以 func(a) 相当于 fail_retry(try_times)(func)(a)
def fail_retry(try_times):
    """
    失败重试的装饰器
    :param try_times:
    :return:
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            number = 0
            while number < try_times:
                number += 1
                print("尝试第:{}次".format(number))
                try:
                    result = func(*args, **kwargs)
                    if result is not None:
                        return result
                    time.sleep(0.1)
                except requests.exceptions.RequestException:
                    time.sleep(0.1)
                    pass
            return None

        return wrapper

    return decorator



@fail_retry(3)
def get_sql_finger_print(sql):
    resp = requests.post('http://localhost:8080/', data=json.dumps({'sql': sql}))
    if resp.status_code >= 200 and resp.status_code < 300:
        return json.loads(resp.text)

    return None

def write_elasticsearch(slow_log):
    es = Elasticsearch('10.37.129.4:9200')
    es.index("mysql_slow_log", doc_type="_doc", body=slow_log)


if __name__ == '__main__':
    logger = logging.getLogger('kafka')
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.INFO)
    kafka_host = '10.37.129.4:9092'
    consumer = KafkaConsumer('slow_query_log',
                            bootstrap_servers=[kafka_host],
                            group_id='python_consumer_1',
                            auto_offset_reset='latest')
    for message in consumer:
       time.sleep(1)
       try:
            val = str(message.value, encoding='utf-8')
            slow_log = json.loads(val)
            data = get_sql_finger_print(slow_log['slowsql'])
            slow_log['finger'] = data['fingerprint']
            slow_log['sql_id'] = data['id']
            'root'.split('_')
            slow_log['schema'] = slow_log['login_user'].split('_')[0]
            write_elasticsearch(slow_log)
       except json.decoder.JSONDecodeError as jde:
           pass