from django.db import models


class BaseModel(models.Model):
    '''所有模型类的抽象基类'''
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_date = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.BooleanField(default=True, verbose_name='删除标记')

    class Meta:
        abstract = True