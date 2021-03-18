import logging

from django.shortcuts import render
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from . import serializer
from . import models
from meiduo.utils import encryption


logger = logging.getLogger('django')


class UserView(CreateAPIView):
    serializer_class = serializer.CreateUserSerialier


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

    serializer_class = serializer.UserDetaiSerializer

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
    serializer_class = serializer.EmailSerializer

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
            return Response({'message':'激活邮箱失败。'}, status=status.HTTP_400_BAD_REQUEST)

        # 修改邮箱激活状态
        user.email_active = True
        user.save()

        # 响应
        return Response({'message': '邮箱激活成功'})

