from django.db import models
from zst_project import common


class SchemaModel(common.CommonModel):
    name = models.CharField(max_length=64, null=False, unique=True, verbose_name='数据库名称',
                            help_text="库的名称，一个库可能有多个实例。最大长度：64字节")
    create_time = models.DateTimeField(auto_now_add=True, blank=True, null=False,
                            verbose_name='数据库创建时间', help_text='数据库创建时间')

    class Meta:
        db_table = 't_db_schema'
        verbose_name = '库表'


class InstanceModel(common.CommonModel):
    MASTER = 'master'
    SLAVE = 'slave'
    ONLINE = 'online'
    OFFLINE = 'offline'
    PENDING = 'pending'
    id = models.BigAutoField(primary_key=True)
    host_ip = models.GenericIPAddressField(max_length=128)
    port = models.IntegerField()
    schema = models.ForeignKey(SchemaModel, to_field='name', db_constraint=False, on_delete=models.CASCADE, related_name='instances')
    role = models.CharField(max_length=64, choices=((MASTER, 'master'), (SLAVE, 'slave')))
    status = models.CharField(max_length=64, null=False, choices=((ONLINE, 'online'), (OFFLINE, 'offline'), (PENDING, 'pending')), default='online')

    class Meta:
        db_table = "t_db_instance"
        verbose_name = '实例表'



class AnsibleTaskResult(common.CommonModel):
    class Status(common.ChoiceEnum):
        Waiting = "waiting"
        Running = "running"
        Success = "success"
        Failed = "failed"
    task_id = models.CharField(max_length=128)
    task_name = models.CharField(max_length=128)
    host = models.CharField(max_length=64)
    result = models.TextField(max_length=65535)
    status = models.CharField(max_length=32, choices=Status, default=Status.Waiting)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)


class AlarmSettingModel(models.Model):
    class Type(common.ChoiceEnum):
        Global = "global"
        Schema = "schema"
        SQL = "sql"
    schema = models.ForeignKey(SchemaModel, to_field='name', db_constraint=False, on_delete=models.CASCADE, null=True, default=None,
                               help_text="库名")
    stop_alarm = models.BooleanField(default=False, help_text="是否停止告警")
    sql_id = models.CharField(max_length=128, null=True, help_text="sql id")
    sql_print = models.TextField(null=True, help_text="sql指纹")
    query_time = models.FloatField(default=0.0, help_text="查询时间阈值")
    query_count = models.IntegerField(default=0, help_text="每分钟出现的次数")
    delete = models.BooleanField(default=False, help_text="逻辑删除标志")
    type = models.CharField(max_length=10, choices=Type, null=False, help_text="设置的类型")

