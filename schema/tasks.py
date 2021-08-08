import os
import shutil
import time
from datetime import datetime

import ansible.constants as C
import redis
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

from .es_document import SlowQuery
from .es_helper import get_aggs, get_results
from .models import *
from .zst_alarm import WexinAlarm

logger = get_task_logger('schema')

@shared_task(bind=True)
def generate_slow_sql(self):
    # TODO 定时产生慢SQL
    # 1. 提前建立好测试表
    # 2. 直接连接上数据库，执行慢SQL
    pass



@shared_task(bind=True)
def install_mysql_by_ansible(self, instance_id):
    task_id = self.request.id
    instance = InstanceModel.objects.get(pk=instance_id)
    try:
        from os.path import dirname, abspath, join
        # base_dir = dirname(dirname(abspath(__file__)))
        # logger.info("Base_dir: %s", base_dir)
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

    logger.info('sources: %s', sources)

    loader = DataLoader()
    inventory = InventoryManager(loader=loader, sources=sources)

    variable_manager = VariableManager(loader=loader, inventory=inventory)

    results_callback = ResultsCollectorJSONCallback(task_id=task_id)

    passwords = dict(vault_pass='')
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


msg_sender = WexinAlarm()

def send_slow_alarm(record):
    # TODO： 加上告警记录
    msg_template = "您的数据库【{}】存在慢SQL: {}，平均执行时间为{}，一分钟执行了{}次，请关注"
    s = SlowQuery.search()
    results = s.filter("term", hash__keyword=record['hash']).execute()
    print(results)
    sql_printer = ""
    if len(results.hits.hits) > 0:
        sql_printer = results.hits.hits[0]['_source']['finger']
    msg = msg_template.format(record['schema'], sql_printer, record['avg_query_time'], record['hash_count'])
    msg_sender.send_msg("ZhangWenBing", msg)

@shared_task
def alarm_minute():
    # 从settings中获取配置信息

    # 告警间隔，单位：秒
    alarm_interval = 60
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    key_name = "slowsql_alarm_end"

    # 默认值
    end = int(time.time())

    if r.exists(key_name):
        end = int(r.get(key_name).decode('utf-8'))

    start = end - alarm_interval

    # 如果end time晚于当前时间，则不运行
    if end > int(time.time()):
        logger.info("slow log alarm shouldn't run at this time, end time is greater than now, end: %d", end)
        return

    # 设置下一次的开始时间
    r.set(key_name, end + alarm_interval)

    global_query_time = 1
    global_query_count = 1

    global_cfg = AlarmSettingModel.objects.filter(type=AlarmSettingModel.Type.Global, delete=False).order_by("-id")
    if global_cfg.exists():
        global_query_time = global_cfg.first().query_time
        global_query_count = global_cfg.first().query_count

    schema_cfg_dict = {}
    schema_cfg_queryset = AlarmSettingModel.objects.filter(delete=False, type=AlarmSettingModel.Type.Schema)
    for schema_cfg in schema_cfg_queryset:
        schema_cfg_dict[schema_cfg.schema.name] = schema_cfg

    sql_cfg_dict = {}
    sql_cfg_queryset = AlarmSettingModel.objects.filter(delete=False, type=AlarmSettingModel.Type.SQL)
    for sql_cfg in sql_cfg_queryset:
        cfg_key = sql_cfg.schema.name + "#" + sql_cfg.sql_id
        sql_cfg_dict[cfg_key] = sql_cfg

    s = SlowQuery.search()

    options = {
        # greater or equal than  -> gte 大于等于
        # greater than  -> gt 大于
        # little or equal thant -> lte 小于或等于
        # 'gte': start,
        # 'lte': end
        'gte': 1627774833000 - 3600000,
        'lte': 1627774833000
    }

    query_start = time.localtime(start)
    query_end = time.localtime(end)

    time_format = "%Y-%m-%d %H:%M:%S"

    logger.info("slow alarm, start: %s, end: %s",
                time.strftime(time_format, query_start),
                time.strftime(time_format, query_end))

    s = s.filter('range', **{'@timestamp': options})
    aggs = {
        "aggs": {
            "schema": {
                "terms": {
                    "field": "schema.keyword"
                },
                "aggs": {
                    "sql_id": {
                        "terms": {
                            "field": "sql_id.keyword"
                        },
                        "aggs": {
                            "avg_query_time": {
                                "avg": {
                                    "field": "query_time_sec"
                                }
                            },
                            "avg_lock_time": {
                                "avg": {
                                    "field": "lock_time_sec"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    get_aggs(s.aggs, aggs)

    result = s.execute().aggregations

    rs = get_results(aggs, result)

    for r in rs:
        threshold_query_time = global_query_time
        threshold_query_count = global_query_count

        cfg = schema_cfg_dict.get(r.get('schema'), None)
        if cfg is not None:
            threshold_query_count = cfg.query_count
            threshold_query_time = cfg.query_time

        sql_cfg = sql_cfg_dict.get(r.get('schema') + "#" + r.get("sql_id"), None)
        if sql_cfg is not None:
            threshold_query_count = sql_cfg.query_count
            threshold_query_time = sql_cfg.query_time

        # 我们在设置告警的时候，threshold_query_count代表的是QPS，所以在具体比较的时候，必须乘以告警间隔时间
        threshold_query_count = threshold_query_count * alarm_interval
        if r['avg_query_time'] > threshold_query_time and r['sql_id_count'] > threshold_query_count:
            logger.info('send slow log, r.avg_query_time: %.2f, threshold_query_time: %.2f, r.sql_id_count: %d, threshold_query_count: %d',
                        r['avg_query_time'], threshold_query_time, r['sql_id_count'], threshold_query_count)
            send_slow_alarm(r)