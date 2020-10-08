from django.contrib import admin
from .models import BillRecord, Category
# Register your models here.


# Blog模型的管理器（自定制显示内容类）
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'path', 'parent_id')


@admin.register(BillRecord)
class BillRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'date', 'category_id')