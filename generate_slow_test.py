import datetime
import hashlib
import json
import random

import requests
from elasticsearch import Elasticsearch
from tqdm import tqdm


def randomtimes(start, end, frmt="%Y-%m-%d"):
    stime = datetime.datetime.strptime(start, frmt)
    etime = datetime.datetime.strptime(end, frmt)
    return random.random() * (etime - stime) + stime


def get_finger_print(sql):
    url = "http://localhost:8080/"

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
        return finger_print["fingerprint"]
    return None

def write_elasticsearch(es, index, slow_log):
    es.index(index, doc_type="_doc", body=slow_log)

if __name__ == '__main__':
    es = Elasticsearch('10.37.129.4:9200')
    fields = ['a', 'b', 'c', 'd', 'e']
    tables = ['T_bill', 'T_user', 'T_money', 'T_computer']
    schema = [
        "test11",
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
        random_time = randomtimes('2021-07-25', '2021-08-10')
        finger_print = get_finger_print(sql)
        data = {
            "slowsql": sql,
            "@timestamp": random_time,
            "query_time_sec": random.random() * 20 + 1,
            "lock_time_sec": random.random() * 20 + 1,
            "rows_sent": int(random.random() * 100000 + 1000),
            "rows_examined": int(random.random() * 100000 + 1000),
            "login_user": random_schema + "_" + random.choice(user),
            "schema": random_schema,
            "finger": finger_print,
            "sql_id": hashlib.md5(finger_print.encode('utf-8')).hexdigest(),
            "is_test": True
        }
        #es_index = datetime.datetime.strftime(random_time, "mysql-slowsql-test-%Y-%m-%d")
        es_index = "mysql_slow_log"
        write_elasticsearch(es, es_index, data)
        pbar.update(1)
    pbar.close()
