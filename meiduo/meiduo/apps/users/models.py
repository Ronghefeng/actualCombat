from django.db import models
from django.contrib.auth.models import AbstractUser

from meiduo.utils.models import BaseModel


class User(AbstractUser):
    """自定义用户类"""

    # verbose_name：admin 站点显示
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    # 定义字段，表示邮箱是否激活，默认未激活
    email_active = models.BooleanField(default=False, verbose_name='邮箱激活状态')
    # 默认收货地址
    default_address = models.ForeignKey('users.Address',
                                        related_name='users',
                                        on_delete=models.SET_NULL,
                                        blank=True,
                                        null=True,
                                        verbose_name='默认收货地址')
    # 外键致使生成的隐式字段：addresses（address_set）

    # Meta：修改模型在 admin 站点显示，以及数据库中存储信息
    class Meta:
        db_table = 'users'
        # 设置模型对象的直观、人类可读的名称
        verbose_name = '用户'
        # 复数名
        verbose_name_plural = verbose_name


class Address(BaseModel):
    """用户收货地址模型"""
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    # 外键致使生成的隐式字段：users（user_set）
    title = models.CharField(max_length=50, verbose_name='地址名称')
    receiver = models.CharField(max_length=50, verbose_name='收货人')
    province = models.ForeignKey('areas.Area', related_name='province', on_delete=models.PROTECT, verbose_name='省')
    city = models.ForeignKey('areas.Area', related_name='city', on_delete=models.PROTECT, verbose_name='市')
    district = models.ForeignKey('areas.Area', related_name='district', on_delete=models.PROTECT, verbose_name='区')
    place = models.CharField(max_length=100, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.EmailField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'address'
        verbose_name = '收货地址'
        verbose_name_plural = verbose_name
        # 指定排序，以更新时间降序
        ordering = ['-update_time']
