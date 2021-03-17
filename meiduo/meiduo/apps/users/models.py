from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class User(AbstractUser):
    """自定义用户类"""

    # verbose_name：admin 站点显示
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')

    # Meta：修改模型在 admin 站点显示，以及数据库中存储信息
    class Meta:
        db_table = 'users'
        # 设置模型对象的直观、人类可读的名称
        verbose_name = '用户'
        # 复数名
        verbose_name_plural = verbose_name