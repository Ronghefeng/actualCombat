from django.db import models


class BaseModel(models.Model):
    """自定义基础模型类"""

    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        # 设置该类只作为抽象类，在执行 makemigrations 和 migrate 时不进行迁移操作
        abstract = True
