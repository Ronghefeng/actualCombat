from rest_framework import serializers

from . import models


class SKUListVIewSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.SKU
        fields = ['id', 'name', 'price', 'sales', 'comments']
