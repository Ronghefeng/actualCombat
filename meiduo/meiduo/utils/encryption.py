# 加密解密模块
import logging

from django.conf import settings

from itsdangerous import TimedJSONWebSignatureSerializer as TJWSignatureSerializer, BadData

from users import constants, models


logger = logging.getLogger('django')


def generate_email_verify_url(user):
    """生成邮箱激活链接"""

    # JSONWebSignatureSerializer(secret-key, expire)
    serializer = TJWSignatureSerializer(settings.SECRET_KEY, 30 * 100)
    # 加密数据
    data = serializer.dumps(
        {
            'user_id': user.id,
            'username': user.username,
            'email': user.email
        }
    ).decode()

    logger.info('encrypted_data=%s', data)

    return constants.EMAIL_VERIFY_URL_PREFIX + 'token=%s' % data


def decipher_user_info(data):
    """解密用户数据"""
    serializer = TJWSignatureSerializer(settings.SECRET_KEY, 30 * 100)

    try:
        user_info = serializer.loads(data)
    except BadData:
        logger.error('解密邮箱激活信息失败。')
        return None

    try:
        user = models.User.objects.get(**user_info)

    except models.User.DoesNotExist:
        logger.error('用户不存在。')
        return None

    return user


