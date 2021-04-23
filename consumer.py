from kafka import KafkaConsumer
from kafka import TopicPartition
import random
import time
import json
import requests
from elasticsearch import Elasticsearch

def write_elasticsearch(slow_log):
    es = Elasticsearch('192.168.33.200:9200')
    es.index("mysql_slow_log", doc_type="_doc", body=slow_log)


if __name__ == '__main__':
    kafka_host = '192.168.33.200:9092'
    consumer = KafkaConsumer(bootstrap_servers=[kafka_host])
    partition = TopicPartition('slow_query_log', 0)
    start = 8833
    end = 8835
    consumer.assign([partition])
    consumer.seek(partition, 19)

    for message in consumer:

        print("got a message", message.offset, )
        val = str(message.value, encoding='utf-8')
        slow_log = json.loads(val)
        print(slow_log)
        url = "http://192.168.33.201:8090/api"

        payload = {
            "sql": slow_log['slowlog.query']
        }
        payload = json.dumps(payload)
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code == 200:
            print(response.text)
            finger_print = json.loads(response.text)
            slow_log["finger_print"] = finger_print["finger_print"]
            if slow_log["slowlog.user"].find("_"):
                slow_log["schema"] = "".split("_")[0]
            else:
                slow_log["schema"] = "UNKNOWN"

            write_elasticsearch(slow_log)

