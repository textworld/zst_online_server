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
