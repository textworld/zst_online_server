from django.db import models


class BaseModel(models.Model):
    id = models.BigAutoField(primary_key=True, )
    gmt_create = models.DateTimeField(auto_now_add=True)
    gmt_update = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
