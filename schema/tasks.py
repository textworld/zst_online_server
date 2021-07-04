import os
import shutil
from datetime import datetime

import ansible.constants as C
import yaml
from ansible import context
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.inventory.manager import InventoryManager
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play import Play
from ansible.plugins.callback import CallbackBase
from ansible.vars.manager import VariableManager
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from git import Repo
import time
from .models import *

logger = get_task_logger('schema')

@shared_task
def add(x, y):
    time.sleep(90)
    return x + y


@shared_task(bind=True)
def install_mysql_by_ansible(self, instance_id):
    task_id = self.request.id
    instance = InstanceModel.objects.get(pk=instance_id)
    try:
        from os.path import dirname, abspath, join
        base_dir = dirname(dirname(abspath(__file__)))
        logger.info("Base_dir: %s", base_dir)
        task = AnsibleTaskResult(task_id=task_id, status=AnsibleTaskResult.Status.Running, result="Start to execute")
        task.save()
        # 通过git，去更新安装脚本
        checkout_playbook(settings.MYSQL_PLAYBOOK_PATH, settings.MYSQL_PLAYBOOK_GIT)
        # 调用ansible_install_api去执行ansible任务
        success = ansible_install_api(task_id, join(settings.MYSQL_PLAYBOOK_PATH, "mysql.yml"), instance)
        # 更新AnsibleTask的状态
        task = AnsibleTaskResult.objects.get(task_id=task_id)
        if success:
            task.status = AnsibleTaskResult.Status.Success
            instance.status = InstanceModel.ONLINE
        else:
            task.status = AnsibleTaskResult.Status.Failed
        task.end_time = datetime.now()
        task.save()
        instance.save()

    except Exception as e:
        logger.error(e)
        raise
    return "success"


def checkout_playbook(p, url):
    if not os.path.exists(p):
        os.mkdir(p)
        Repo.clone_from(url, p)

    if not os.path.isdir(p):
        return False

    repo = Repo(p)

    repo.remote("origin").pull()

# 调用ansible的API，
# 返回值： 成功，True; 失败, False
def ansible_install_api(task_id, play_book_path, instance):
    context.CLIARGS = ImmutableDict(connection='smart', private_key_file=settings.ANSIBLE_PRIVATE_KEY, forks=10,
                                    become_method='sudo', become_user='root', check=False, diff=False, verbosity=0)

    host_list = [instance.host_ip]
    sources = ','.join(host_list)
    if len(host_list) == 1:
        sources += ','

    loader = DataLoader()
    passwords = dict(vault_pass='ffffff')

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
        play_book['vars']['mysql_port'] = instance.port
        play_book['vars']['mysql_schema'] = instance.schema.name
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