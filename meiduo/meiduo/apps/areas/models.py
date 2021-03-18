from django.db import models

# Create your models here.
class Area(models.Model):
    """省市区模型类"""

    name = models.CharField(max_length=50, verbose_name='名称')
    # 自关联字段：Area 与 Area 为 1 对 多关系，来表示 省-市-区 之间的关联关系
    # 在 1 对 多 的关系中，会在 1 的模型表中隐式的创建一个字段 area_set（模型类名小写_set），related_name 可以修改该字段默认名称
    # null 表示数据库中否允许为空；blank 表示表单中是否允许为空；
    # 设置两个字段的目的：某些场景下数据库中不允许存入 NULl，但是在表单填写时可以不填写，此时数据库存储的是一个空字符串，而非 NULL
    parent = models.ForeignKey('self',
                               on_delete=models.SET_NULL,
                               related_name='subs',
                               null=True,
                               blank=True,
                               verbose_name='上级行政区划')

    class Meta:
        db_table = 'areas'
        verbose_name = '行政区划'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name