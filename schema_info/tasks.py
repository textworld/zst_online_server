# 名字一定要取成tasks.py 否则，celery是无法自动发现
from celery import shared_task, Task
from time import sleep
from datetime import datetime
from celery.utils.log import get_task_logger
from .models import MySQLInstance, AnsibleTaskResult
from celery import chain, group

import json
import shutil

import ansible.constants as C
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.module_utils.common.collections import ImmutableDict
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play import Play
from ansible.plugins.callback import CallbackBase
from ansible.vars.manager import VariableManager
from ansible import context
from django.conf import settings
import yaml

logger = get_task_logger('schema_info')


# Create a callback plugin so we can capture the output
class ResultsCollectorJSONCallback(CallbackBase):
    """A sample callback plugin used for performing an action as results come in.

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin.
    """

    def __init__(self, task_id=None, schema_id=None, *args, **kwargs):
        super(ResultsCollectorJSONCallback, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}
        self.task_id = task_id
        self.schema_id = schema_id
        self.is_failed = False

    def save_log(self, msg, status=None):
        task = AnsibleTaskResult.objects.get(task_id=self.task_id)
        task.result = task.result + "\n" + msg
        if status:
            task.status = status
        task.save()

    def runner_on_failed(self, host, res, ignore_errors=False):
        if not ignore_errors:
            self.is_failed = True
        self.save_log('FAILED: %s %s, ignores: %s' % (host, res, ignore_errors))

    def runner_on_ok(self, host, res):
        self.save_log('OK: %s %s' % (host, res))

    def runner_on_skipped(self, host, item=None):
        self.save_log('SKIPPED: %s' % host)

    def runner_on_unreachable(self, host, res):
        self.is_failed = True
        self.save_log('UNREACHABLE: %s %s' % (host, res))

# 调用ansible的API，
# 返回值： 成功，True; 失败, False
def ansible_install_api(task_id, play_book_path, schema):
    context.CLIARGS = ImmutableDict(connection='smart', private_key_file=settings.ANSIBLE_PRIVATE_KEY, forks=10,
                                    become_method='sudo', become_user='root', check=False, diff=False, verbosity=0)

    host_list = [schema.host_ip]
    sources = ','.join(host_list)
    if len(host_list) == 1:
        sources += ','

    loader = DataLoader()
    passwords = dict(vault_pass='')

    results_callback = ResultsCollectorJSONCallback(task_id=task_id)

    inventory = InventoryManager(loader=loader, sources=sources)

    variable_manager = VariableManager(loader=loader, inventory=inventory)
    tqm = TaskQueueManager(
        inventory=inventory,
        variable_manager=variable_manager,
        loader=loader,
        passwords=passwords,
        stdout_callback=results_callback,  # Use our custom callback instead of the ``default`` callback plugin, which prints to stdout
    )

    play_sources = []

    import os
    os.chdir(os.path.dirname(play_book_path))
    with open(play_book_path) as f:
        data = yaml.load(f, yaml.SafeLoader)
        if isinstance(data, list):
            play_sources.extend(data)
        else:
            play_sources.append(data)

    logger.info("there are %d tasks to run", len(play_sources))
    for play_book in play_sources:
        play_book['hosts'] = host_list
        play_book['remote_user'] = 'vagrant'
        play_book['vars']['mysql_port'] = schema.port
        play_book['vars']['mysql_schema'] = schema.schema
        print("playbook", play_book)
        play = Play().load(play_book, variable_manager=variable_manager, loader=loader)
        # Actually run it
        try:
            result = tqm.run(play)  # most interesting data for a play is actually sent to the callback's methods
        finally:
            # we always need to cleanup child procs and the structures we use to communicate with them
            logger.info("tqm has finished")
            tqm.cleanup()
            if loader:
                loader.cleanup_all_tmp_files()

    # Create play object, playbook objects use .load instead of init or new methods,
    # this will also automatically create the task objects from the info provided in play_source

    # Remove ansible tmpdir
    shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)
    return not results_callback.is_failed

@shared_task
def periodic_check_mysql():
    # instances = MySQLSchema.objects.filter(status=MySQLSchema.ONLINE).all()
    logger.info("periodic_check_mysql")
    # instances = [{"id": i} for i in range(100)]
    # fn = group(check_mysql_alive.si(i['id']) for i in instances)
    # fn()
    # return "success"
    c = chain(check_mysql_alive.si(1) | check_mysql_thread_count.si(1))
    c.delay()  # c() 同步调用
    # result = c.delay()
    # result.get() 同步


@shared_task
def check_mysql_alive(schema_id):
    sleep(1)
    logger.info("check alive for schema_id [%d]", schema_id)


@shared_task
def check_mysql_thread_count(schema_id):
    sleep(5)
    logger.info("check thread count success")


@shared_task
def add(x, y):
    logger.info("got a request")
    sleep(10)
    return x + y


class MyTask(Task):
    def on_success(self, retval, task_id, args, kwargs):
        print("task success")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print("task failure")


@shared_task(bind=True, base=MyTask)
def install_mysql_by_ansible(self, schema_id):
    # xxxxxx
    # 执行ansible脚本去安装mysql
    task_id = self.request.id
    schema = MySQLInstance.objects.get(pk=schema_id)
    try:
        from os.path import dirname, abspath, join
        base_dir = dirname(dirname(abspath(__file__)))
        logger.info("Base_dir: %s", base_dir)
        task = AnsibleTaskResult(task_id=task_id, status=AnsibleTaskResult.Status.Running, result="Start to execute")
        task.save()
        success = ansible_install_api(task_id, join(base_dir, "ansible-playbook/mysql.yml"), schema)
        task = AnsibleTaskResult.objects.get(task_id=task_id)
        if success:
            task.status = AnsibleTaskResult.Status.Success
        else:
            task.status = AnsibleTaskResult.Status.Failed
        task.end_time = datetime.now()
        task.save()
    except Exception as e:
        logger.error(e)
        raise
    return "success"


# Good
@shared_task
def check_mysql(schema_id):
    MySQLInstance.objects.get(pk=schema_id)
    # 通过python去尝试连接对应的mysql实例，如果连接失败，则进行告警

    return "success"


