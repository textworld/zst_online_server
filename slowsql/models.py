from django.db import models
from schema_info.models import MySQLSchema

# Create your models here.
class AlarmSettingModel(models.Model):
    schema = models.ForeignKey(MySQLSchema, db_constraint=False, on_delete=models.CASCADE, null=True, default=None)
    stop_alarm = models.BooleanField(default=False)
    sql_print_hash = models.CharField(max_length=128)
    sql_print = models.TextField()
    query_time = models.FloatField()
    query_count = models.IntegerField()
    delete = models.BooleanField(default=False)