from django.db import models
from enum import Enum, EnumMeta

class BaseModel(models.Model):
    id = models.BigAutoField(primary_key=True, )
    gmt_create = models.DateTimeField(auto_now_add=True)
    gmt_update = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


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