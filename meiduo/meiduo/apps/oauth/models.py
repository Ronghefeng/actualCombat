from django.db import models

from meiduo.utils.models import BaseModel
from users.models import User

class OAuthQQUser(BaseModel):
    """QQ 授权模型"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    # QQ 返回的用户 openid，db_index=True 表示为该字段建立索引
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)

    class Meta:
        db_table = 'qquser'
        verbose_name = 'QQ 用户登录数据'
        verbose_name_plural = verbose_name
