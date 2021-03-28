import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.mixins import CacheResponseMixin

from . import models
from .serializer import AreaSerializer, AreaDetialSerializer


logger = logging.getLogger('django')

class AreaListViewV1(APIView):
    """获取所有省的数据 v1.0"""

    # 暂时避免认证
    # authentication_classes = []

    def get(self, request):

        # assert 断言表达式为真，否则抛出 AssertionError 异常
        # assert self.request is None, ('assert self.request is None')

        logger.info('Get areas list by v1 api.')

        # 获取所有省数据的 queryset
        # 数据库中省的上级为NULL
        provinces = models.Area.objects.filter(parent=None)

        # 创建序列化器，将数据进行序列化
        # 由于查询的为所有省，因此需要指定 many=True
        serializer = AreaSerializer(provinces, many=True)

        # 响应
        return Response(serializer.data)


class AreaListViewV2(ListAPIView):
    """
    获取所有省的数据 v2.0
    视图中实现的方法是 get_list，在 ListAPIView 已有相同实现
    """
    # ListAPIView 继承了 GenericAPIView
    # 使用 GenericAPIView 需要指定 queryset、serializer 等必须参数
    queryset = models.Area.objects.filter(parent=None)
    serializer_class = AreaSerializer


class AreaDetailViewV1(APIView):
    """查询省市区详细数据"""

    authentication_classes = []

    def get(self, request, pk):
        """pk 为 省、市、区（县）的 id"""

        logger.info('Get areas detail by v1 api.')

        try:
            area = models.Area.objects.get(pk=pk)

        except models.Area.DoesNotExist:
            return Response({'message': 'Invalid pk.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AreaDetialSerializer(area)

        return Response(serializer.data)


class AreaDetailViewV2(RetrieveAPIView):
    """
    查询省市区详细数据 v2.0
    在此视图中主要功能为根据 pk 获取单条数据，在 RetrieveAPIView 中已有相同实现
    """

    # RetrieveAPIView 继承了 GenericAPIView
    # 使用 GenericAPIView 需要指定 queryset、serializer 等必须参数
    # 由于当前业务，获取单条信息时，也需要返回 subs（pk = parent） 的数据，
    # 有一个自关联的需求，因此 queryset 可以直接给 all，无需过滤
    queryset = models.Area.objects.all()
    serializer_class = AreaDetialSerializer


class AreaViewSet(CacheResponseMixin, ReadOnlyModelViewSet):
    """
    获取省市区信息 v3.0
    在有多中需求的情况下可以考虑使用视图集
    当前视图需要提供的功能：get_list 和 get_detail，ReadOnlyModelViewSet 中已存在同样实现
    ReadOnlyModelViewSet 继承了 GenericViewSet，需要提供必须参数 queryset 和 serializer_class
    但是 get_list 和 get_detail 所需要的 queryset 和 serializer 不同，
    无法通过设置 queryset 和 serializer_class 来满足不同需求，
    可以通过重写 GenericViewSet 中的 get_queryset 和 get_serializer 来满足需求
    *** 使用视图集需要对路由做修改，例如 as_view({'get': 'list})，对不同请求做方法映射
    *** 也可以通过 DefaultRouter 来注册路由，达到同样效果
    """

    authentication_classes = []

    def get_queryset(self):
        """根据不同需求，获取不同数据集"""

        # 如果请求的行为是 list，则是请求所有的省信息，反之则是请求某个省的信息
        # ViewSetMixin 会在 initialize_request 方法中根据请求类型设置 self.action 的值，表示该方法的行为
        if self.action == 'list':
            return models.Area.objects.filter(parent=None)

        return models.Area.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return AreaSerializer

        return AreaDetialSerializer

