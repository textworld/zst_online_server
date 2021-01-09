import os

from celery import Celery, platforms

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zst_project.settings')

app = Celery('zst_project')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # 'chekc-every-30': {
    #     'task': 'schema_info.tasks.periodic_check_mysql',
    #     'schedule': 30,
    # },
    # 'fetch-proxy-10': {
    #     'task': 'news.tasks.periodic_fetch_proxy_from_zhima',
    #     'schedule': 10
    # },
    # 'scrap_dbaplus-10': {
    #     'task': 'news.tasks.scrap_news',
    #     'schedule': 10
    # }
    'slowsql_alarm': {
        'task': 'slowsql.tasks.alarm_minute',
        'schedule': 10
    }
}

platforms.C_FORCE_ROOT = True
