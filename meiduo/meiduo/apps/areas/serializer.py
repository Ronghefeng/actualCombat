import logging

from rest_framework import serializers


from . import models


logger = logging.getLogger('django')


class AreaSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Area
        # 指定需要序列化的字段
        fields = ['id', 'name']


class AreaDetialSerializer(serializers.ModelSerializer):

    # 需要序列化 pk 作为 parent_id 的数据
    # subs 是模型中获取外键表的字段
    # subs = serializers.PrimaryKeyRelatedField() # 只会序列化 id
    # subs = serializers.StringRelatedField() # 序列化的是模型类中 __str__ 方法返回的值
    subs = AreaSerializer(many=True)

    class Meta:
        model = models.Area
        fields = ['id', 'name', 'subs']

