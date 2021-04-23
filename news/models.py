from django.db import models


# Create your models here.
class ProxyModel(models.Model):
    ip = models.GenericIPAddressField()
    port = models.IntegerField()
    expire_time = models.DateTimeField()
    city = models.CharField(max_length=64)
    isp = models.CharField(max_length=64)
    call_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)


class NewsModel(models.Model):
    title = models.CharField(max_length=128)
    url = models.TextField()
    hash = models.CharField(max_length=128)
    insert_time = models.DateTimeField(null=True, auto_now_add=True)