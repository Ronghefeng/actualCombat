from django.db import models


class BaseModel(models.Model):

    created_time = models.DateTimeField(auto_now_add=True, verbose_name='created_time')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='updated_name')

    class Meta:
        abstract = True