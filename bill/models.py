from django.db import models
from zst_project.models import BaseModel
# Create your models here.


class Category(BaseModel):
    label = models.CharField(max_length=128, unique=True, help_text='分类名称', verbose_name='分类名称')
    path = models.TextField(max_length=1000, help_text='路径，以/分割', verbose_name='路径，以/分割')
    parent_id = models.BigIntegerField(default=0)

    @classmethod
    def create_cate(cls, label, parent_id):
        parent_cate_id = 0
        parent_cate_path = "/"
        if parent_id:
            if cls.objects.filter(pk=parent_id).exists():
                parent_cate = cls.objects.get(pk=parent_id)
                parent_cate_path = parent_cate.path + "/"
                parent_cate_id = parent_cate.id
        cate = cls(label=label, parent_id=parent_cate_id, path=parent_cate_path + label)
        return cate

    @classmethod
    def update_path(cls, cate_id):
        if cls.objects.filter(pk=cate_id).exists():
            cate = cls.objects.get(pk=cate_id)
            parent_path = "/"
            if cate.parent_id > 0:
                parent_cate = cls.objects.get(pk=cate.parent_id)
                parent_path = parent_cate.path + "/"
            cate.path = parent_path + cate.label
            cate.save()
        elif cate_id > 0:
            return
        cates = cls.objects.filter(parent_id=cate_id)
        for son_cate in cates:
            cls.update_path(son_cate.id)

class BillRecord(BaseModel):
    name = models.CharField(max_length=128, help_text='记录名称', verbose_name='记录名称', null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    date = models.DateField(null=False)
    category_id = models.ForeignKey('Category', null=True, blank=True, on_delete=models.SET_NULL, db_constraint=False)

    class Meta:
        unique_together = ('name', 'price', 'date')
