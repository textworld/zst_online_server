from django.db import models
from django.core.exceptions import ValidationError

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
    task_id = models.CharField(max_length=128) # celery 的task_id
    task_name = models.CharField(max_length=128) # ansible的task name
    host = models.CharField(max_length=64) # 对应的host
    result = models.TextField(max_length=65535) # 结果
    status = models.CharField(max_length=32) # 状态



# Create your models here.
class MySQLSchema(CommonModel):
    MASTER = 'master'
    SLAVE = 'slave'
    ONLINE = 'online'
    OFFLINE = 'offline'
    PENDING = 'pending'
    id = models.BigAutoField(primary_key=True)
    host_ip = models.GenericIPAddressField(max_length=128)
    port = models.IntegerField()
    schema = models.CharField(max_length=64)
    role = models.CharField(max_length=64, choices=((MASTER, 'master'), (SLAVE, 'slave')))
    status = models.CharField(max_length=64, null=False, choices=((ONLINE, 'online'), (OFFLINE, 'offline'), (PENDING, 'pending')), default='online')
    phy_host = models.ForeignKey(Host, null=True, on_delete=models.PROTECT, db_constraint=False)

    class Meta:
        db_table = "mysql_schema"

    def __str__(self):
        return "MySQLSchema-{}-{}-{}-{}".format(self.host_ip, self.port, self.schema, self.role)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        exists = MySQLSchema.objects.filter(
            host_ip=self.host_ip,
            port=self.port,
            schema=self.schema,
            role=self.role).exists() # objects是一个模型管理器，默认的模型管理
        if exists:
            raise ValidationError("repeat data for " + str(self))

        super().save(force_insert=force_insert, force_update=force_update, using=using,update_fields=update_fields)