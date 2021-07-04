from __future__ import absolute_import, unicode_literals
import os
from celery import Celery, platforms


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zst_project.settings.dev')

app = Celery('zst_project')
app.config_from_object(os.environ.get('DJANGO_SETTINGS_MODULE'), namespace='CELERY')
app.autodiscover_tasks()
platforms.C_FORCE_ROOT = True


app.conf.beat_schedule = {
   'chekc-every-30': {
       'task': 'schema.tasks.check_mysql',
       'schedule': 30,
       'args': (1,)
   }
}