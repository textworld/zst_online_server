from django.db import models
from rest_framework.pagination import PageNumberPagination
from enum import Enum, EnumMeta


# 基础表，包含了gmt_update 和gmt_create两个字段
class CommonModel(models.Model):
    gmt_update = models.DateTimeField(auto_now=True, null=True)
    gmt_create = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        abstract = True


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = 'page_num'
    max_page_size = 500


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