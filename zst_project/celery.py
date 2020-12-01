from __future__ import absolute_import, unicode_literals
import os
from celery import Celery, platforms
from datetime import timedelta
from celery.schedules import crontab
import django
import os, sys

path=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zst_project.settings')
django.setup()

#app = Celery('zst_project', broker=redis_endpoint)
app = Celery('zst_project')

#app.config_from_object('django.conf:settings', namespace='CELERY')
app.config_from_object('django.conf:settings')


app.conf.update(
    CELERYBEAT_SCHEDULE={
        'sum-task': {
            'task': 'deploy.tasks.add',
            'schedule':  timedelta(seconds=20),
            'args': (5, 6)
        },
        'send-report': {
            'task': 'deploy.tasks.report',
            'schedule': crontab(hour=4, minute=30, day_of_week=1),
        }
    }
)


app.autodiscover_tasks()

platforms.C_FORCE_ROOT = True

