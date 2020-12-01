from __future__ import absolute_import, unicode_literals
import os
from celery import Celery, platforms

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zst_project.settings')

redis_endpoint = 'redis://192.168.31.32:16379/0'
app = Celery('zst_project', broker=redis_endpoint)

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

platforms.C_FORCE_ROOT = True

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))