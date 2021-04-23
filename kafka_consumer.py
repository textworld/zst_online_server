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
    #group_id = "python_consumer_" + str(random.randint(1, 1000))
    #group_id = "python_consumer_same_group_id_3"
    print("Group_id: {}".format(group_id))
    consumer = KafkaConsumer('slow_query_log',
                             bootstrap_servers=[kafka_host],
                             group_id=group_id,
                             auto_offset_reset='latest')
    for message in consumer:
        # message.value byte[]
        # str unicode
        # network str -> byte[]
        # receive from network byte[]
        # str()
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
            write_elasticsearch(slow_log)

