import logging
from decimal import Decimal

from django_redis import get_redis_connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView

from cards import constents
from goods import models as goodsmodels
from . import serializer as order_serializer


logger = logging.getLogger('django')

class OrderSettlementView(APIView):
    """
    订单处理视图
    """

    # 设置权限，只有登录用户才可以查询订单详情
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """查询订单页面"""

        # 1、获取当前用户
        user = request.user
        # 2、创建 redis 连接
        redis_conn = get_redis_connection('carts')
        # 3、从 redis 获取购物车 sku_id
        skus = {}

        carts_info_key = constents.USER_CARTS_INFO_HASH_KEY + str(user.id)
        selected_info_key = constents.USER_CARTS_INFO_SET_KEY + str(user.id)

        sku_info = redis_conn.hgetall(carts_info_key)

        for sku_id, count in sku_info.items():
            # 只获取选中的商品
            if redis_conn.sismember(selected_info_key, sku_id):
                skus[int(sku_id)] = int(count)

        # 4、根据 sku_id 获取对应商品信息，对 sku 对象新增 count 属性，表示商品的件数
        sku_obj_list = goodsmodels.SKU.objects.filter(id__in=skus.keys())

        for sku_obj in sku_obj_list:
            sku_obj.count = skus[sku_obj.id]

        # 5、新增返回字段：运费，同商品信息封装
        # 注意：金钱类的数据均使用 decimal 类型
        # 一般运费根据业务需求定

        ret = {
            # 运费
            'freight': Decimal('10.00'),
            'skus': sku_obj_list
        }

        # 6、创建序列化器，对数据进行序列化
        # 序列化的对象包括：dict、list、queryset、model。。。
        # 此处由于将需要序列化的数据封装至一个字典中，因此无需设置 many=True
        serializer = order_serializer.OrderSerializer(ret)

        # 7、响应
        return Response(serializer.data)


class CommitOrderView(CreateAPIView):
    """定义订单提交视图"""
    serializer_class = order_serializer.CommitOrderSerializer

    permission_classes = [IsAuthenticated]

