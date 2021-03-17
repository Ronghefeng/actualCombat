import logging
from random import randint

from django_redis import get_redis_connection
from django.http.response import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from . import constants
from meiduo.libs.yuntongxun.sms import CCP
from celery_tasks.sms.tasks import send_sms_codes


logger = logging.getLogger('django')

class SMSCode(APIView):

    def get(self, request, mobile):
        """
        获取请求 url 中手机号，生成验证码
        1、根据 url 中匹配到的手机号，生成随机的验证码
        2、创建 redis 连接对象，将 手机-验证码 保存到 redis 数据库缓存
        3、利用容联云通讯发送验证码到手机
        3、返回响应
        """
        # 建立 redis 连接
        redis_conn = get_redis_connection('verify_codes')

        # 避免手机重复发送，发送验证码之前需要检查是否已经发送过
        if redis_conn.get('sms_flag_%s' % mobile):
            return Response({'message': '该手机验证码已发送。'}, status=status.HTTP_400_BAD_REQUEST)

        # %06d 表示 6 位数字，不够则补 0
        sms_codes = '%06d' % randint(0, 999999)
        logger.info('sms_codes= %s', sms_codes)

        # setex(key, value, expire)
        key = 'mobile_%s' % mobile
        flag_key = 'sms_flag_%s' % mobile

        # 保存手机号及验证码
        # redis_conn.setex(key, constants.SMS_CODES_EXPIRE_TIME, sms_codes)

        # 记录手机发送标识
        # redis_conn.setex('sms_flag_%s' % mobile, constants.SMS_SEND_FLAG_EXPIRE_TIME, constants.SMS_SEND_FLAG)

        # 利用 redis 管道（pipleline）优化两次设置操作，减少 redis 的连接次数
        # pipeline 支持将多个命令放置管道中，待 pipeline.execute() 执行时，一次执行全部命令
        pl = redis_conn.pipeline()

        # pipeline 填充命令
        pl.setex(key, constants.SMS_CODES_EXPIRE_TIME, sms_codes)
        pl.setex(flag_key, constants.SMS_SEND_FLAG_EXPIRE_TIME, constants.SMS_SEND_FLAG)

        logger.info('key= %s, value= %s', key, redis_conn.get(key))

        # 执行 pipeline（管道）
        pl.execute()

        # 发送短信
        # [sms_codes, 5]：[key, time]，设置有效时间为 5 分钟
        # ccp = CCP()
        # ccp.send_template_sms(mobile, [sms_codes, constants.SMS_CODES_EXPIRE_TIME // 60], constants.CCP_TEMPLATE)

        # 使用 celery 任务队列改写 发送短信 功能
        # 触发异步任务，将异步任务添加到任务队列
        send_sms_codes.delay(mobile, sms_codes)

        return Response({'message': '已发送短信至用户'})


def test(request, *args, **kwargs):
    logger.info(args)
    return JsonResponse({'message': 'test'})
