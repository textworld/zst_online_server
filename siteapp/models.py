from django.db import models
from user.models import ZstUser
# ip代理表
class ProxyModel(models.Model):
    ip = models.GenericIPAddressField()
    port = models.IntegerField()
    expire_time = models.DateTimeField()
    city = models.CharField(max_length=64)
    isp = models.CharField(max_length=64)
    call_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)

    class Meta:
        db_table = "t_ip_proxy"
        verbose_name = 'ip代理'


# 新闻列表
class NewsModel(models.Model):
    title = models.CharField(max_length=128)
    url = models.TextField()
    hash = models.CharField(max_length=128)
    insert_time = models.DateTimeField(null=True, auto_now_add=True)

    class Meta:
        db_table = 't_news_list'
        verbose_name = '新闻'


# 操作记录
class HistoryOpModel(models.Model):
    user = models.CharField(max_length=128, verbose_name='操作用户')
    op_module = models.CharField(max_length=128, verbose_name='操作模块')
    log = models.TextField(verbose_name='日志')
    op_time = models.DateTimeField(verbose_name='操作时间', auto_now_add=True)
    class Meta:
        db_table = 't_history_op'
        verbose_name = '操作记录'