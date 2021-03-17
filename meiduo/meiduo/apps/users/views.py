import logging

from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from . import serializer
from . import models


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


