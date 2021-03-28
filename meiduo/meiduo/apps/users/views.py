from datetime import datetime
import logging

from django_redis import get_redis_connection
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework import mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import ObtainJSONWebToken

from .serializer import CreateUserSerialier, UserDetaiSerializer, EmailSerializer, AddressSerializer, AddressTitleSerializer
from . import serializer
from . import models
from meiduo.utils import encryption
from . import constants
from goods import models as goodsmodels, serializer as goodsserializer
from cards.utils import merge_cookie_cart_into_redis


jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER

logger = logging.getLogger('django')


class UserView(CreateAPIView):
    """注册用户"""
    serializer_class = CreateUserSerialier


class UsernameCheckView(APIView):
    """前端输入用户名时，校验用户名是否已注册"""

    def get(self, request, username):
        """
        获取前端传递的 username，去数据库检查是否已存在
        前端通过判断 count 大小来区分注册用户名是否已存在
        """
        logger.info('username = %s', username)

        count = models.User.objects.filter(username=username).count()

        data = {
            'username': username,
            'count': count
        }

        return Response(data)


class MobileCheckView(APIView):
    """检查手机号是否已注册"""

    def get(self, request, mobile):
        logger.info('mobile = %s', mobile)

        count = models.User.objects.filter(mobile=mobile).count()

        data = {
            'mobile': mobile,
            'count': count
        }

        return Response(data)


class UserDetailView(RetrieveAPIView):
    """用户中心展示，访问的是单条数据，因此选择继承 RetrieveAPIView"""

    serializer_class = UserDetaiSerializer

    # 此写法会在 get_object 方法中调用 get_queryset，会将模型对应数据集全部提取出来
    # 当前采用手段是重写 get_object 方法，不再通过查询数据库获取，提高性能
    # queryset = models.User.objects.all()

    # 指定用户权限，只有通过认证的用户才能访问该视图
    # IsAuthenticated 检查用户是否已登录，采用 Django 原生认证方法
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # 在 django 的 View.as_view(view) 中设置 self.request
        # 由于该视图设置了访问权限，因此通过 request 可以直接获取对象信息，而不需要再通过 queryset 去查询数据库获取
        return self.request.user


class EmailView(UpdateAPIView):
    """此视图用于处理更新邮箱请求"""

    # 权限：仅允许已登录用户设置邮箱
    permission_classes = [IsAuthenticated]
    # 指定序列化器
    serializer_class = EmailSerializer

    def get_object(self):
        return self.request.user


class EmailVerifyView(APIView):
    """邮箱激活验证回调视图"""
    permission_classes = []
    authentication_classes = ''

    def get(self, request):

        # 获取前端传入的加密数据
        user_info = request.query_params.get('token')
        if not user_info:
            return Response({'message': '请传入 token。'}, status=status.HTTP_400_BAD_REQUEST)

        # 解密数据，获取用户
        user = encryption.decipher_user_info(user_info)

        # 检查用户是否存在
        if not user:
            return Response({'message': '激活邮箱失败。'}, status=status.HTTP_400_BAD_REQUEST)

        # 修改邮箱激活状态
        user.email_active = True
        user.save()

        # 响应
        return Response({'message': '邮箱激活成功'})


class AddressView(GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin):
    """
    收货地址视图
    1、新增地址
        请求：POST localhost:8000/addresses/
        由于 CreateModelMixin 中的 create 不满足需求，此处根据业务重写，对于地址数量进行上限限制
    2、查询当前用户所有收货地址
        请求：GET localhost:8000/addresses/
        继承 ListModelMixin 实现
    3、修改地址信息
        请求：PUT localhost:8000/addresses/3/
        继承 UpdateModelMixin 实现
    4、删除地址
        请求： DELETE localhost:8000/addresses/3/
        业务需求为逻辑删除，因此需要重写 destroy 方法
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer

    def create(self, request):
        """
        添加收货地址
        测试数据：
        {
            "province_id": 430000,
            "city_id": 430200,
            "district_id": 430223,
            "title": "默认",
            "receiver": "rhf",
            "place": "盘比",
            "mobile": 15757337126,
            "tel": "",
            "email": "2427219623@qq.com"
        }
        """

        # 根据业务需求，收货地址不能超过 20 条
        user = request.user
        if user.addresses.all().count() >= constants.MAX_ADDRESS_COUNT:
            return Response({'message': '收货地址已经超过 20 条，不允许再添加'}, status=status.HTTP_400_BAD_REQUEST)

        # 创建序列化器
        serializer = self.get_serializer(data=request.data)
        # 校验数据
        serializer.is_valid(raise_exception=True)
        # 保存模型对象
        serializer.save()
        # 响应，返回序列化数据 serializer.data
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        """
        业务场景：返回指定用户的所有收货地址
        需要对数据集进行过滤，Address.objects.all() 会返回所有用户的收货地址
        """
        # return models.Address.objects.filter(user=self.request.user, is_deleted=False)
        return self.request.user.addresses.filter(is_deleted=False)

    def destroy(self, request, *args, **kwargs):
        # 物理删除
        # models.Address.objects.filter(**kwargs).delete()
        # 逻辑删除，因为在 get_queryset 对 is_deleted=False 数据有进行过滤

        # 获取请求 address 对象
        # try:
        #     addr_obj = models.Address.objects.get(**kwargs)
        # except models.Address.DoesNotExist:
        #     return Response({'message': '改地址已被删除'}, status=status.HTTP_400_BAD_REQUEST)
        addr_obj = self.get_object()

        addr_obj.is_deleted = True
        addr_obj.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['put'], detail=True)
    def title(self, request, pk=None):
        """
        自定义修改某个值时的请求，需要添加装饰器
        detail 指定是否必须传入 pk
        methods 指定请求类型
        由于制定了前端必须传入 pk，这里的响应方法必须有 pk 参数，否则参数个数不匹配
        请求格式：
            PUT localhost:8000/addresses/<pk>/tile
        """
        addr_obj = self.get_object()

        # 更新 addr_obj 对象的 title
        # 由于只修改 title，前端仅传入 title 即可，因此不可以用 AddressSerializer 序列化器
        serializer = AddressTitleSerializer(instance=addr_obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @action(methods=['put'], detail=True)
    def state(self, request, pk=None):
        """
        响应设置默认地址的请求
        请求方式：
            PUT localhost:8000/address/<pk>/state/
        """

        # 拿到 pk 指定的地址 address
        address = self.get_object()

        # 将 user 的 default_address 设置为 address 保存
        request.user.default_address = address
        request.user.save()
        # 响应
        return Response({'message': '设置默认地址成功！'})


class UserBrowserHistoryView(CreateAPIView):
    """保存用户浏览记录"""

    serializer_class = serializer.UserBrowserHistoryViewSerializer
    # 只保存已登录用户的浏览记录
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        取出用户浏览记录
            1、获取当前请求用户
            2、建立 redis 连接
            3、查询用户浏览记录的 sku_id
            4、根据 sku_id 获取 sku 对象列表，需要保证浏览记录的顺序，在前端展示时，最前面的是最新的浏览
            5、序列化 sku 对象列表
            6、响应
        注意：
            当前 get 并没有使用到分页，因此全局设置的分页配置在当前 get 方法中无效
        """

        user_id = request.user.id

        redis_conn = get_redis_connection('browser_history')

        key = constants.USER_BROWSER_HISTORY_KEY + str(user_id)

        # 切记，从 redis 取出的 list 中的元素会转换为 bytes
        sku_id_list = redis_conn.lrange(key, 0, -1)

        # 此方式取出数据的顺序不会按照 sku_id_list 中元素的顺序
        # sku_obj_list = goodsmodels.SKU.objects.filter(id__in=sku_id_list)
        sku_obj_list = []
        for sku_id in sku_id_list:

            try:
                # 此处 sku_id 会自动从 bytes 类型转为字符型，因此不会报错
                sku_obj = goodsmodels.SKU.objects.get(pk=sku_id)

            except goodsmodels.SKU.DoesNotExist:
                pass
            else:
                sku_obj_list.append(sku_obj)

        serializer = goodsserializer.SKUListVIewSerializer(sku_obj_list, many=True)

        return Response(serializer.data)


class UserAuthView(ObtainJSONWebToken):
    """自定义用户登录视图"""

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)
            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() +
                              api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    token,
                                    expires=expiration,
                                    httponly=True)

            # 合并购物车
            merge_cookie_cart_into_redis(request, user, response)

            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

