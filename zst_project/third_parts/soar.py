from django.conf import settings
import requests
import json
import logging

def get_sql_id(sql):
    resp = requests.post(settings.SOAR_URL, json={'sql': sql})
    if resp.status_code >= 200 and resp .status_code < 300:
       return json.loads(resp.text)
    logging.error('failed to make request to soar: [%s]', resp.text)
    return None