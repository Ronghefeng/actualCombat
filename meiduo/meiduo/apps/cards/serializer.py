from rest_framework import serializers


from goods import models as goodsmodels


class CartsViewSerializer(serializers.Serializer):

    sku_id = serializers.IntegerField(label='sku_id', min_value=1)
    count = serializers.IntegerField(label='加购数量')
    # 为商品是否选中设置一个默认值
    selected = serializers.BooleanField(label='是否选中商品', default=True)

    def validate_sku_id(self, value):
        """对 sku_id 进行校验"""
        try:
            sku = goodsmodels.SKU.objects.get(pk=value)

        except goodsmodels.SKU.DoesNotExist:
            raise serializers.ValidationError('Invalid sku_id.')

        return value


class SKUCartSerializer(serializers.ModelSerializer):

    count = serializers.IntegerField(label='加购数量')
    selected = serializers.BooleanField(label='是否选中商品')

    class Meta:
        model = goodsmodels.SKU
        fields = [
            'id',
            'name',
            'caption',
            'goods',
            'category',
            'price',
            'sales',
            'comments',
            'default_image_url',
            'count',
            'selected'
        ]


class CartDeleteSerializer(serializers.Serializer):
    sku_id = serializers.IntegerField(label='sku_id', min_value=1)

    def validate_sku_id(self, value):
        """对 sku_id 进行校验"""
        try:
            sku = goodsmodels.SKU.objects.get(pk=value)

        except goodsmodels.SKU.DoesNotExist:
            raise serializers.ValidationError('Invalid sku_id.')

        return value


class CartSelectionSerializer(serializers.Serializer):
    selected = serializers.BooleanField(label='是否选中商品')