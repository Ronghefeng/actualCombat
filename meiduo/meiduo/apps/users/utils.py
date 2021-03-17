import re

from django.contrib.auth.backends import ModelBackend

from . import models


def jwt_response_payload_handler(token, user=None, request=None):
    """自定义 JWT 的 payload"""
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }


def get_account_user(username):
    """根据用户获取 user"""

    # 需要对用户名进行一定限制，例如不能以数字开头，否则以下校验规则无法区分手机号和用户名
    keyword = 'username'

    # 判断是否输入的是手机号
    if re.match(r'1[3-9]\d{9}$', username):
        keyword = 'mobile'

    keywords = {
        keyword: username
    }

    try:
        user = models.User.objects.get(**keywords)

    except models.User.DoesNotExist:
        return None

    return user


class MutiAccountLoginBackend(ModelBackend):
    """
    修改 Django 原有的用户登录认证逻辑，支持用户名、手机号、邮箱等多账号登录
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        """获取用户"""

        user = get_account_user(username)

        if user and user.check_password(password):
            return user



