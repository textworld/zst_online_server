from django.db import models
from django.core.exceptions import ValidationError
import datetime
from enum import Enum, EnumMeta

from django.contrib.auth.backends import BaseBackend

class ChoiceEnumMeta(EnumMeta):

    def __getattribute__(cls, name):
        attr = super().__getattribute__(name)
        if isinstance(attr, Enum):
            return attr.value
        return attr

    def __iter__(self):
        return ((tag.value, tag.name) for tag in super().__iter__())


class ChoiceEnum(Enum, metaclass=ChoiceEnumMeta):
    """
    Enum for Django ChoiceField use.
    """
    pass

# Create your models here.
# 基础表，包含了gmt_update 和gmt_create两个字段
class CommonModel(models.Model):
    gmt_update = models.DateTimeField(auto_now=True, null=True)
    gmt_create = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        abstract = True


# 表示MySQL实例所在的物理机
class Host(CommonModel):
    name = models.CharField(max_length=30)
    memory = models.CharField(max_length=30)
    cpu = models.CharField(max_length=30)

    def __str__(self):
        return f"Host: {self.id}-{self.name}-{self.memory}-{self.cpu}"

class AnsibleTaskResult(CommonModel):
    class Status(ChoiceEnum):
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


class DbSchema(CommonModel):
    name = models.CharField(max_length=64, null=False, unique=True, verbose_name='数据库名称',
                            help_text="库的名称，一个库可能有多个实例。最大长度：64字节")
    create_time = models.DateTimeField(auto_now_add=True, blank=True, null=False,
                            verbose_name='数据库创建时间', help_text='数据库创建时间')

    class Meta:
        db_table = 't_db_schema'
        verbose_name = '数据库表'


class MySQLInstance(CommonModel):
    MASTER = 'master'
    SLAVE = 'slave'
    ONLINE = 'online'
    OFFLINE = 'offline'
    PENDING = 'pending'
    id = models.BigAutoField(primary_key=True)
    host_ip = models.GenericIPAddressField(max_length=128)
    port = models.IntegerField()
    schema = models.ForeignKey(DbSchema, to_field='name', db_constraint=False, on_delete=models.CASCADE, related_name='instances')
    role = models.CharField(max_length=64, choices=((MASTER, 'master'), (SLAVE, 'slave')))
    status = models.CharField(max_length=64, null=False, choices=((ONLINE, 'online'), (OFFLINE, 'offline'), (PENDING, 'pending')), default='online')
    phy_host = models.ForeignKey(Host, null=True, on_delete=models.PROTECT, db_constraint=False)

    class Meta:
        db_table = "t_db_instance"

    def __str__(self):
        return "MySQLSchema-{}-{}-{}-{}".format(self.host_ip, self.port, self.schema, self.role)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        exists = MySQLInstance.objects.filter(
            host_ip=self.host_ip,
            port=self.port,
            schema=self.schema,
            role=self.role).exists() # objects是一个模型管理器，默认的模型管理
        if exists:
            raise ValidationError("repeat data for " + str(self))

        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

