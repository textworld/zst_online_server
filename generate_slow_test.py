import random
import datetime
from elasticsearch import Elasticsearch
from tqdm import tqdm
import json
import requests
import hashlib


def randomtimes(start, end, frmt="%Y-%m-%d"):
    stime = datetime.datetime.strptime(start, frmt)
    etime = datetime.datetime.strptime(end, frmt)
    return random.random() * (etime - stime) + stime


def get_finger_print(sql):
    url = "http://192.168.33.201:8090/api"

    payload = {
        "sql": sql
    }
    payload = json.dumps(payload)
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        finger_print = json.loads(response.text)
        return finger_print["finger_print"]
    return None

def write_elasticsearch(es, index, slow_log):
    es.index(index, doc_type="_doc", body=slow_log)

if __name__ == '__main__':
    es = Elasticsearch('192.168.33.200:9200')
    fields = ['a', 'b', 'c', 'd', 'e']
    tables = ['T_bill', 'T_user', 'T_money', 'T_computer']
    schema = [
        "test",
        "Murray",
        "Noe",
        "Jameson",
        "Dallin",
        "Ena",
        "Sonia",
        "Luigi",
        "Veronica",
        "Leon",
        "Gage",
        "Guillermo",
        "Talia",
        "Gaetano",
        "Tania",
        "Arnoldo",
        "Zelda",
        "Orie",
        "Ana"
    ]
    user = ["root", "test", "mysql", "dba", "dev1", "dev2", "dev3"]
    sql_list = []

    total = 20000
    pbar = tqdm(total=total)
    for i in range(total):
        # random.randint(1,10) [1, 10]
        table_idx = random.randint(0, len(tables) - 1)
        field_num = random.randint(1, len(tables))
        where_list = []
        for j in range(field_num):
            where_list.append(random.choice(["and", "or"]))
            where_list.append("{} {} '{}'".format(
                random.choice(fields),
                random.choice(["like", "="]),
                "".join(random.sample('zyxwvutsrqponmlkjihgfedcba', random.randint(1, 10)))))
        sql = "select * from {} where {};".format(tables[table_idx], " ".join(where_list[1:]))
        random_schema = random.choice(schema)
        random_time = randomtimes('2019-12-01', '2020-12-27')
        finger_print = get_finger_print(sql)
        data = {
            "query_sql": sql,
            "@timestamp": random_time,
            "query_time": random.random() * 20 + 1,
            "lock_time": random.random() * 20 + 1,
            "rows_sent": int(random.random() * 100000 + 1000),
            "rows_examined": int(random.random() * 100000 + 1000),
            "user": random_schema + "_" + random.choice(user),
            "schema": random_schema,
            "host": "192.168.31.55",
            "finger": finger_print,
            "hash": hashlib.md5(finger_print.encode('utf-8')).hexdigest()
        }
        es_index = datetime.datetime.strftime(random_time, "mysql-slowsql-test-%Y-%m-%d")
        write_elasticsearch(es, es_index, data)
        pbar.update(1)
    pbar.close()
