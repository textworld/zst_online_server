from django.db import models


# 课程
class Course(models.Model):
    title = models.CharField(max_length=128, help_text='课程名称', verbose_name='课程名称')
