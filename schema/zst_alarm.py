import json
import logging
import time

import requests

# Get an instance of a logger
logger = logging.getLogger(__name__)


class WexinAlarm:
    def __init__(self):
        self.token = ""
        self.expired = int(time.time())

    def refresh_token(self):
        now = int(time.time())
        if now < self.expired and len(self.token) > 0:
            return
        # TODO 配置写到配置文件中
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=ww2ef294fd1f043429&corpsecret=deLb5gd4hiP-l5ekwbEZ6h1WZbGz43VPOWgqwRrfqIM"

        response = requests.request("GET", url, headers={}, data={})

        if response.status_code > 300:
            logger.error("error status code for weixin token: %d", response.status_code)
            return

        resp_obj = json.loads(response.text)
        if resp_obj['errcode'] != 0:
            logger.error("failed to get token: %s", resp_obj['errmsg'])
            return

        self.token = resp_obj['access_token']
        self.expired = int(time.time()) + resp_obj['expires_in']

    def send_msg(self, users, msg):
        self.refresh_token()
        url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + self.token

        payload = {
            "touser": users,
            "toparty": "1",
            "msgtype": "text",
            "agentid": 1000002,
            "text": {
                "content": msg
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
        if resp.status_code >= 300:
            logger.error('failed to send message to wechat: %s', resp.text)
