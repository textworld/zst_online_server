# 名字一定要取成tasks.py 否则，celery是无法自动发现
from celery import shared_task, Task
from time import sleep
from celery.utils.log import get_task_logger
from .models import MySQLSchema

logger = get_task_logger('schema_info')

@shared_task
def add(x, y):
    logger.info("got a request")
    sleep(10)
    return x + y

class MyTask(Task):
    def on_success(self, retval, task_id, args, kwargs):
        print("task success")
        schema_id = args[0]
        mysql_instance = MySQLSchema.objects.get(pk=schema_id)
        mysql_instance.status = MySQLSchema.ONLINE
        mysql_instance.save()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print("task failure")


@shared_task(base=MyTask)
def install_mysql_by_ansible(schema_id):
    # xxxxxx
    # 执行ansible脚本去安装mysql

    return "success"

# Good
@shared_task
def check_mysql(schema_id):
    MySQLSchema.objects.get(pk=schema_id)
    # 通过python去尝试连接对应的mysql实例，如果连接失败，则进行告警

    return "success"

# # Bad: orm object
# def check_mysql(schema):
