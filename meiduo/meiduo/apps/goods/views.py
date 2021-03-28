import logging

from rest_framework.generics import ListAPIView
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination

from . import models
from . import serializer


class SKUListView(ListAPIView):
    """
    获取指定 category_id 的所有 SKU
    localhost:8000/categories/115/skus/?page=4
    注意：有参数的请求地址最后不需要加"/"
    """

    serializer_class = serializer.SKUListVIewSerializer

    # 排序，使用 filter_backends 定义过滤方式为排序过滤 OrderingFilter
    filter_backends = [OrderingFilter]
    # 指定排序字段，设置了 ordering_fields，则前端无需设置 ordering 参数
    # ordering_fields = ['create_time', 'price', 'sales']

    # 分页，可在全局 REST_FRAMEWORK 中设置，也可对每个接口进行设置
    # pagination_class = PageNumberPagination

    def get_queryset(self):
        """
        由于需要获取所有 SKU，因此采用 ListAPIView，
        但是业务需求是获取指定的 category_id 下，且已经上架(is_launched=True)的 SKU，
        因此需要对 query_set 进行过滤，通过 query_set 属性设置不符合要求
        """

        # 如果在当前视图没有定义 get/post 等方法接收 url 提取出来的参数，可以利用视图对象的 args/kwargs 来接收
        # args 在参数没有起别名定义时接收参数，kwargs 在参数有别名定义时接收，
        # 例如 /(?P<pk>\d+)/ 给路径参数定义了别名 pk，/user/\d+/$ 没有为传入的数值定义别名，因此用 args 接收
        category_id = self.kwargs.get('category_id')

        return models.SKU.objects.filter(is_launched=True, category_id=category_id)

