from .base import *

CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = "Asia/Shanghai"
CELERY_TASK_TIME_LIMIT = 30 * 60

ANSIBLE_PRIVATE_KEY = "~/.ssh/id_rsa"

SOAR_URL = 'http://127.0.0.1:8080'