from django.db import models
from db.base_model import BaseModel
from django.contrib.auth.models import AbstractUser


class User(AbstractUser, BaseModel):
    class Meta:
        db_table = 'userinfo'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class AddressManager(models.Manager):
    def get_default_addr(self, user):
        try:
            default_addr = self.get(user=user, is_default=True)
        except UserAddress.DoesNotExist:
            default_addr = None
        return default_addr


class UserAddress(BaseModel):
    recipient = models.CharField(max_length=20, verbose_name='收件人')
    contact_num = models.CharField(max_length=11, verbose_name='联系电话')
    address = models.CharField(max_length=100, verbose_name='收件人地址')
    zip_code = models.IntegerField(null=True, verbose_name='邮政编码')
    is_default = models.BooleanField(default=False, verbose_name='是否默认')
    user = models.ForeignKey(User, verbose_name='所属账户')
    objects = AddressManager()
    class Meta:
        db_table = 'address'
        verbose_name = '地址'
        verbose_name_plural = verbose_name
