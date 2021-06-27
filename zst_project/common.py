from django.db import models

# 基础表，包含了gmt_update 和gmt_create两个字段
class CommonModel(models.Model):
    gmt_update = models.DateTimeField(auto_now=True, null=True)
    gmt_create = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        abstract = True

