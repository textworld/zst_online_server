from celery import shared_task
from time import sleep
from celery.utils.log import get_task_logger
logger = get_task_logger('schema_info')
from .models import MySQLSchema

@shared_task
def add(x, y):
    return x + y


@shared_task
def send_mail(addr, user):
    n = MySQLSchema.objects.create(host_ip="127.0.0.1", port=3306, schema="test", role="master", status=MySQLSchema.OFFLINE)
    logger.info("n id: %d", n.id)
    logger.info("had send mail: %s %s", addr, user)
    print("sssssfdf")
    return "success"
