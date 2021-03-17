import logging

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from . import utils
from .serializer import QQOAuthSerializer
from oauth.models import OAuthQQUser
from meiduo.utils import auth


logger = logging.getLogger('django')

class QQOAuthURLView(APIView):

    def get(self, request):
        """
        1、取出前端传入的 next（标记用户原始请求地址）作为 state 参数
        2、获取 QQ 登录网址
        3、因为需要前端通过浏览器去请求地址，展示扫码授权界面，因此需要返回 URL
        """
        state = request.query_params.get('next', '/')

        data_dict = {
            'client_id': settings.QQ_CLIENT_ID,
            'client_secret': settings.QQ_CLIENT_SECRET,
            'state': state,
            'redirect_url': settings.QQ_REDIRECT_URL
        }

        qq_auth = utils.OAuthQQ(**data_dict)
        qq_auth_url = qq_auth.get_authorization_code_url()

        logger.info('授权请求地址：%s', qq_auth_url)

        return Response({'qq_auth_url': qq_auth_url})


class QQOAuthView(APIView):
    """获取前端传入 code，请求 QQ 服务器获取 openid"""

    def get(self, request):
        code = request.query_params.get('code', None)

        if code is None:
            return Response('请传入 code。')

        data_dict = {
            'client_id': settings.QQ_CLIENT_ID,
            'client_secret': settings.QQ_CLIENT_SECRET,
            'redirect_url': settings.QQ_REDIRECT_URL
        }
        qq_auth = utils.OAuthQQ(**data_dict)

        # 获取 access_token
        try:
            access_token = qq_auth.get_access_token(code)
        except Exception as e:
            logger.error('获取 Access Token 失败，错误信息：%s' % e)
            return Response({'err_msg': 'QQ 服务器不可用。'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 获取 openid
        try:
            openid = qq_auth.get_openid(access_token)
        except Exception as e:
            logger.error('获取 openid 失败，错误信息：%s' % e)
            return Response({'err_msg': 'QQ 服务器不可用。'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 检查 openid 是否已有用户绑定
        try:
            qq_user = OAuthQQUser.objects.get(openid=openid)

        except OAuthQQUser.DoesNotExist:
            # openid 未和用户绑定过
                # 1、创建一个新用户来绑定此 openid
                # 2、将 openid 返回，前端另外发起一个请求，进行用户绑定
            return Response({'openid': openid})

        else:
            # 如果 openid 已绑定用户，则返回用户登录信息
            user = qq_user.user
            token = auth.generate_token(user)

            # 返回用户信息，及登录状态凭证
            return Response({'openid': openid, 'token': token, 'user_id': user.id})

    def post(self, request):
        """处理用户绑定 openid"""

        # 创建序列化器，对请求数据进行反序列化
        serializer = QQOAuthSerializer(data=request.data)

        # 调用序列化器 is_valid 进行数据校验
        serializer.is_valid(raise_exception=True)

        # 获取 user，调用序列化器的 save 方法
        user = serializer.save()

        # 生成 jwt 进行状态保存
        token = auth.generate_token(user)

        # 返回响应
        return Response({
            'token': token,
            'user_id': user.id,
            'username': user.username
        })


