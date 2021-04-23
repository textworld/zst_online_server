from django.db import models
from schema_info.models import MySQLSchema
from zst_project.models import ChoiceEnum


# Create your models here.
class AlarmSettingModel(models.Model):
    class Type(ChoiceEnum):
        Global = "global"
        Schema = "schema"
        SQL = "SQL"
    schema = models.ForeignKey(MySQLSchema, db_constraint=False, on_delete=models.CASCADE, null=True, default=None)
    stop_alarm = models.BooleanField(default=False)
    sql_print_hash = models.CharField(max_length=128, null=True)
    sql_print = models.TextField()
    query_time = models.FloatField(default=0.0)
    query_count = models.IntegerField(default=0)
    delete = models.BooleanField(default=False)
    type = models.CharField(max_length=10, choices=Type, null=True)