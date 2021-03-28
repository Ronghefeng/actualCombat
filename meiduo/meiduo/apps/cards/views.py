import logging
import base64, pickle

from django_redis import get_redis_connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from . import constents
from .serializer import CartsViewSerializer, SKUCartSerializer, CartDeleteSerializer, CartSelectionSerializer
from goods import models as goodsmodels

logger = logging.getLogger('django')


class CartsViewV1(APIView):
    """
    购物车视图 v1.0
    """
    def _get_redis_conn(self):
        return get_redis_connection('carts')

    def perform_authentication(self, request):
        """
        根据业务场景，需要考虑用户已登录和未登录两种情况下添加购物车行为
        由于在 settings 中已经设置全局的认证：DEFAULT_AUTHENTICATION_CLASSES
        因此未登录用户无法到达视图，通过重写 perform_authentication 方法，延迟认证，
        直到调用 request.user 或者 request.auth 时才进行认证
        """
        pass

    def is_valid(self, serializer):
        serializer.is_valid(raise_exception=True)

    def get_validated_data(self, serializer):

        self.is_valid(serializer)

        # 获取校验后的数据
        return (serializer.validated_data.get('sku_id'),
                serializer.validated_data.get('count'),
                serializer.validated_data.get('selected'))

    def post(self, request, *args, **kwargs):

        serializer = CartsViewSerializer(data=request.data)
        sku_id, count, selected  = self.get_validated_data(serializer)

        user = self.get_user(request)

        if user:
            # 1、判断用户购物车信息在 redis 中是否存有，已有则进行增量添加
            # 2、将购物车信息分别用 hash 和 set 保存，
            # 3、hash
            #     key: {sku_id: count}
            # 4、set
            #     key: (sku_id_1, sku_id_2,....)
            redis_conn = self._get_redis_conn()

            pl = redis_conn.pipeline()

            key = constents.USER_CARTS_INFO_HASH_KEY + str(user.id)

            # hincrby(key, field, increament)
            # key 或者 field 不存在时则会进行创建，field 存在则会对 filed 值添加 increament
            pl.hincrby(key, sku_id, count)

            if selected:
                # 如果选中了，则将该 sku_id 保存到 set 中
                key = constents.USER_CARTS_INFO_SET_KEY + str(user.id)

                pl.sadd(key, sku_id)

            pl.execute()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # 用户未登录，将数据存入 cookie
        # 1、取出 cookie，判断 cookie 中是否已有购物车的数据
        # 2、如果有则进行增量修改，没有则赋值
        # 存入 cookie 的购物车数据结构如下：
            # cookie = {
            #     'carts': {
            #         'sku_id': {
            #             'count': 1,
            #             'selected': true
            #         }
            #     }
            # }
        carts = request.COOKIES.get('carts', {})

        if carts:
            # 从 cookie 中取出来的为 字符串，需要进行反序列化
            try:
                carts = self.decode_cookie(carts)
            except Exception as e:
                logger.error('解码错误，错误信息=%s' % e)
                return Response({'message': '解码错误。'}, status=status.HTTP_400_BAD_REQUEST)

            # cookie 中已有购物车数据
            if sku_id in carts:
                count += carts['sku_id'].get('count', 0)

        carts[sku_id] = {
            'count': count,
            'selected': selected
        }

        try:
            carts = self.encode_cookie(carts)
        except Exception as e:
            logger.error('编码错误，错误信息=%s' % e)
            return Response({'message': '编码错误。'}, status=status.HTTP_400_BAD_REQUEST)

        response = Response(serializer.data, status=status.HTTP_201_CREATED)
        response.set_cookie('carts', carts)

        return response

    def decode_cookie(self, data):
        """对 cookie 中提取的字符串转换为 python 对象"""

        # 把字符串转换为 bytes 类型的字符串
        str_bytes = data.encode()
        # 把 bytes 类型的字符串转换为 bytes 类型
        bytes_obj = base64.b64decode(str_bytes)
        # 把 bytes 类型转换为 Python 对象
        obj = pickle.loads(bytes_obj)

        return obj

    def encode_cookie(self, obj):
        """将 python 字典转换成字符串"""

        # 把 python 对象转换为 bytes 类型
        bytes_obj = pickle.dumps(obj)
        # 把 bytes 类型转为 bytes 类型字符串
        bytes_str = base64.b64encode(bytes_obj)
        # 把 bytes 类型字符串转为 json 字符串
        json_str = bytes_str.decode()

        return json_str

    def get_user(self, request):
        # 通过 request.user 判断用户是否登录，已登录数据存入 redis，未登录数据存入 cookie
        # user.is_authenticated：检查用户认证是否通过，因为未认证情况 Django 可能会置为匿名用户
        try:
            user = request.user

            if not user.is_authenticated:
               user = None

        except:
            user = None

        return user

    def get(self, request, *args, **kwargs):
        user = self.get_user(request)

        carts = {}

        if user:
            redis_conn = self._get_redis_conn()
            # 1、取出用户的购物车数据
            # 2、封装数据，同 cookie 中存储格式一致，方便序列化
            selected_key = constents.USER_CARTS_INFO_SET_KEY + str(user.id)
            # 取出 set 中的数据
            selected_info = redis_conn.smembers(selected_key)
            # 取出 hash 中的数据
            carts_key = constents.USER_CARTS_INFO_HASH_KEY + str(user.id)
            carts_info = redis_conn.hgetall(carts_key)

            for sku_id, count in carts_info.items():
                carts[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in selected_info
                }

        else:
            carts = request.COOKIES.get('carts', {})

            if not carts:
                return Response({'message': '购物车为空'})

            carts = self.decode_cookie(carts)

        sku_list = self.packaging_data(carts)
        # 序列化对象
        serializer = SKUCartSerializer(sku_list, many=True)

        return Response(serializer.data)

    def packaging_data(self, data):
        # 取出 sku 对象
        sku_list = goodsmodels.SKU.objects.filter(id__in=data.keys())

        # 为每个 sku 对象添加临时属性 count 和 selected，进行序列化，用于页面展示
        for sku in sku_list:
            sku.count = data[sku.id].get('count')
            sku.selected = data[sku.id].get('selected')

        return sku_list

    def put(self, request, *args, **kwargs):
        # 获取序列化器
        serializer = CartsViewSerializer(data=request.data)
        # 调用序列化器校验数据，获取校验后的数据
        sku_id, count, selected  = self.get_validated_data(serializer)
        # 判断用户是否登录
        user = self.get_user(request)
        # 用户已登录，去 redis 修改数据
        if user:
            # 创建 redis 连接
            redis_conn = self._get_redis_conn()
            pl = redis_conn.pipeline()
            # 修改 hash 中的数据：hset(key, field, value)
            carts_info_key = constents.USER_CARTS_INFO_HASH_KEY + str(user.id)
            pl.hset(carts_info_key, sku_id, count)
            # 判断 selected 是否为 True
            selected_info_key = constents.USER_CARTS_INFO_SET_KEY + str(user.id)
            if selected:
                # 为 True，将 sku_id 加入 set
                pl.sadd(selected_info_key, sku_id)
            # 不为 True，将 sku_id 从 set 中移除
            else:
                pl.srem(selected_info_key, sku_id)

            return Response(serializer.data)

        # 用户未登录，修改 cookie
        carts = request.COOKIES.get('carts')

        if not carts:
            return Response({'err_msg': '购物车为空，请求错误。'}, status=status.HTTP_400_BAD_REQUEST)

        # 解密 cookie 数据
        carts = self.decode_cookie(carts)
        # 直接修改 cookie
        carts[sku_id] = {
            'count': count,
            'selected': selected
        }
        # 加密修改后的 cookie
        carts = self.encode_cookie(carts)
        # 生成 response
        response = Response(serializer.data)
        # 设置 response 的 cookie
        response.set_cookie('carts', carts)
        # 响应
        return response

    def delete(self, request, *args, **kwargs):
        """
        删除购物车商品信息，由于前端只需要传入 sku_id 即可，因此选择重写一个序列化器 CartDeleteSerializer 比较合适
        """
        serializer = CartDeleteSerializer(data=request.data)
        self.is_valid(serializer)

        sku_id = serializer.validated_data.get('sku_id')

        user = self.get_user(request)

        if user:
            redis_conn = self._get_redis_conn()
            pl = redis_conn.pipeline()

            carts_info_key = constents.USER_CARTS_INFO_HASH_KEY + str(user.id)
            pl.hdel(carts_info_key, sku_id)

            selected_info_key = constents.USER_CARTS_INFO_SET_KEY + str(user.id)
            pl.srem(selected_info_key, sku_id)

            # 删除所有数据
            # redis_conn.delete(carts_info_key, selected_info_key)
            pl.execute()

            return Response(status=status.HTTP_204_NO_CONTENT)

        carts = request.COOKIES.get('carts', {})

        if not carts:
            return Response({'err_msg': 'Cookie 中没有购物车数据。'}, status=status.HTTP_400_BAD_REQUEST)

        carts = self.decode_cookie(carts)

        # 判断需要删除的 sku_id 是否在 cookie 中
        if sku_id not in carts.keys():
            return Response({'err_msg': 'Cookie 中没有该商品数据。'}, status=status.HTTP_400_BAD_REQUEST)

        carts.pop(sku_id)

        response = Response(status=status.HTTP_400_BAD_REQUEST)

        # 如果 cookie 中已经没有任何购物车信息，可以将该 cookie 删除
        if not len(carts.keys()):
            # 删除 cookie
            response.delete_cookie('carts')

        return response


class CartSelectedAllVIew(APIView):
    """购物车全选视图"""

    def perform_authentication(self, request):
        """
        根据业务场景，需要考虑用户已登录和未登录两种情况下添加购物车行为
        由于在 settings 中已经设置全局的认证：DEFAULT_AUTHENTICATION_CLASSES
        因此未登录用户无法到达视图，通过重写 perform_authentication 方法，延迟认证，
        直到调用 request.user 或者 request.auth 时才进行认证
        """
        pass

    def get_user(self, request):
        # 通过 request.user 判断用户是否登录，已登录数据存入 redis，未登录数据存入 cookie
        # user.is_authenticated：检查用户认证是否通过，因为未认证情况 Django 可能会置为匿名用户
        try:
            user = request.user

            if not user.is_authenticated:
               user = None

        except:
            user = None

        return user

    def _get_redis_conn(self):
        return get_redis_connection('carts')

    def put(self, request, *args, **kwargs):

        serializer = CartSelectionSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        selected = serializer.validated_data.get('selected')

        user = self.get_user(request)

        if user:
            redis_conn = self._get_redis_conn()

            carts_info_key = constents.USER_CARTS_INFO_HASH_KEY + str(user.id)
            sku_id_list = redis_conn.hkeys(carts_info_key)

            selected_info_key = constents.USER_CARTS_INFO_SET_KEY + str(user.id)

            # for sku_id in sku_id_list:
            #
            #     if selected:
            #         redis_conn.sadd(selected_info_key, sku_id)
            #         continue
            #
            #     redis_conn.srem(selected_info_key, sku_id)
            if not selected:
                redis_conn.srem(selected_info_key, *sku_id_list)

            else:
                redis_conn.sadd(selected_info_key, *sku_id_list)

            return Response(serializer.data)

        carts = request.COOKIES.get('carts', {})

        if not carts:
            return Response({'err_msg': 'Cookie 中没有购物车数据。'}, status=status.HTTP_400_BAD_REQUEST)

        carts = self.decode_cookie(carts)

        for sku_id in carts.keys():
            carts[sku_id]['selected'] = selected

        carts = self.encode_cookie(carts)

        response = Response(serializer.data)
        response.set_cookie('carts', carts)

        return response

    def decode_cookie(self, data):
        """对 cookie 中提取的字符串转换为 python 对象"""

        # 把字符串转换为 bytes 类型的字符串
        str_bytes = data.encode()
        # 把 bytes 类型的字符串转换为 bytes 类型
        bytes_obj = base64.b64decode(str_bytes)
        # 把 bytes 类型转换为 Python 对象
        obj = pickle.loads(bytes_obj)

        return obj

    def encode_cookie(self, obj):
        """将 python 字典转换成字符串"""

        # 把 python 对象转换为 bytes 类型
        bytes_obj = pickle.dumps(obj)
        # 把 bytes 类型转为 bytes 类型字符串
        bytes_str = base64.b64encode(bytes_obj)
        # 把 bytes 类型字符串转为 json 字符串
        json_str = bytes_str.decode()

        return json_str

