from celery import shared_task
from time import sleep
from celery.utils.log import get_task_logger
from datetime import datetime

logger = get_task_logger('schema_info')
from .models import MySQLSchema
from celery import Task, chain, group


class MyTask(Task):
    def on_success(self, retval, task_id, args, kwargs):
        print('task done: {0}'.format(retval))
        return super(MyTask, self).on_success(retval, task_id, args, kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print('task fail, reason: {0}'.format(exc))
        return super(MyTask, self).on_failure(exc, task_id, args, kwargs, einfo)

@shared_task
def add(x, y):
    return x + y


@shared_task(base=MyTask)
def send_mail(addr, user):
    #n = MySQLSchema.objects.create(host_ip="127.0.0.1", port=3306, schema="test", role="master", status=MySQLSchema.OFFLINE)
    #logger.info("n id: %d", n.id)
    logger.info("had send mail: %s %s", addr, user)
    print("sssssfdf")
    return "success"

@shared_task
def tttt(a, b):
    logger.info("tttt")
    return "success"

@shared_task(bind=True)
def check_mysql(self, schema_id):
    logger.info("schema_id: %d", schema_id)
    sleep(schema_id)
    return "success"

@shared_task()
def check_mysql_group():
    fn = group(check_mysql.s(i) for i in range(10))
    print(fn().get())


