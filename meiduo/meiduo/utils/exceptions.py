# 由于 REST framework 无法处理例如mysql、redis等数据库异常，需要自定义一个异常捕获
import logging

from django.db import DatabaseError
from redis.exceptions import RedisError
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status


# 调用日志器
logger = logging.getLogger('django')


def exception_handler(exc, context):
    """
    自定义异常处理
    :param exec: 异常实例对象
    :param context: 抛出异常的上下文
    :return: Response 响应对象
    """

    # 调用 DRF 框架原生的异常处理方法
    response = drf_exception_handler(exc, context)

    if response is None:
        view = context['view']

        # 判断是否处于数据库异常
        if isinstance(exc, DatabaseError) or isinstance(exc, RedisError):
            logger.error('[%s] %s' % (view, exc))
            response = Response({'message': 'Mysql 或 Redis 数据库异常'}, status=status.HTTP_507_INSUFFICIENT_STORAGE)

    return response