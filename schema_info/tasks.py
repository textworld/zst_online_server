from celery import shared_task
from time import sleep
from celery.utils.log import get_task_logger
logger = get_task_logger('schema_info')
import logging


@shared_task
def add(x, y):
    return x + y


@shared_task
def send_mail(addr, user):

    sleep(1)
    logger.info("had send mail", addr, user)
    logging.INFO("ssssss")
    print("sssssfdf")
    return "success"
