from celery import shared_task, Task
from time import sleep
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
import yaml
import logging
import sys

logger = logging.getLogger("test")
logger.setLevel(logging.DEBUG)

# 创建一个流处理器handler并设置其日志级别为DEBUG
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)

# 创建一个格式器formatter并将其添加到处理器handler
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

# 为日志器logger添加上面创建的处理器handler
logger.addHandler(handler)

class ResultsCollectorJSONCallback(CallbackBase):
    """A sample callback plugin used for performing an action as results come in.

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin.
    """

    def __init__(self, task_id = None, schema_id=None, *args, **kwargs):
        super(ResultsCollectorJSONCallback, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}
        self.task_id = task_id
        self.schema_id = schema_id

    def v2_runner_on_unreachable(self, result):
        host = result._host
        self.host_unreachable[host.get_name()] = result
        logger.error("runner unreachable")

    def v2_runner_on_ok(self, result, *args, **kwargs):
        logger.info("Task %s success", result.task_name)

    def runner_on_skipped(self, host, item=None):
        logger.info("task skipped")
        print(host, item)

    def runner_on_failed(self, host, res, ignore_errors=False):
        print(res)
        logger.info("Task  failed")

def ansible_install_api(task_id, play_book_path, schema):
    context.CLIARGS = ImmutableDict(connection='smart', private_key_file="~/.ssh/id_rsa", forks=10,
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
        play_book['vars']['schema_name'] = schema.schema
        print(play_book)
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

if __name__ == '__main__':
    from os.path import join, dirname, abspath
    from collections import namedtuple
    Schema = namedtuple('Schema', ['host_ip', 'port', 'schema'])
    schema = Schema('10.37.129.3', 4000, 'testss')
    base_dir = dirname(dirname(abspath(__file__)))
    print(base_dir)

    ansible_install_api(1, join(base_dir, "ansible-playbook/mysql.yml"), schema)