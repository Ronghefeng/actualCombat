import logging

from django_redis import get_redis_connection
from rest_framework import serializers

from users.models import User
from .models import OAuthQQUser


logger = logging.getLogger('django')

class QQOAuthSerializer(serializers.Serializer):
    # 定义需要反序列化的字段

    # 当前 mobile 使用 RegexField，是因为采用的序列化起继承的 Serializer，
    # 可以自定义字段类型，在 ModelSerializer 中由于制定了绑定模型，因此采用的模型中字段类型直接转换
    # RegexField 定义一个正则匹配字段，regex 定义正则匹配规则
    mobile = serializers.RegexField(label='手机号', regex=r'1[3-9]\d{9}$')

    openid = serializers.CharField(label='openid')
    password = serializers.CharField(label='密码', min_length=8, max_length=20)
    sms_codes = serializers.CharField(label='手机验证码')

    def validate(self, attrs):
        """定义校验规则"""
        logger.info('Enter into validate function,attrs=%s', attrs)

        # 获取 前端传入 openid，对加密的 openid 进行解密，openid 在请求时使用 itsdangrous 加密技术，本次未使用
        try:
            openid = attrs.pop('openid', None)
        except KeyError:
            raise serializers.ValidationError('Invalid openid.')

        # 进行解密。。。
        # 将解密后的 openid 重新加入 attrs
        attrs['openid'] = openid

        # 校验手机验证码验证码
        attrs = self.check_sms_codes(attrs)

        # 检查该手机号是否已经有注册用户，有则进行绑定
        try:
            user = User.objects.get(mobile=attrs.get('mobile'))

        except User.DoesNotExist:
            # 用户不存在
            pass

        else:
            # 如果用户已存在，则检查密码是否正确
            if not user.check_password(attrs.get('password')):
                raise serializers.ValidationError('Invalid password.')

            # 如果 user 存在，且密码正确，则将 user 添加到 attrs 中，以备后续反序列化绑定
            attrs['user'] = user

        return attrs

    def check_sms_codes(self, attrs):
        """校验验证码"""

        redis_conn = get_redis_connection('verify_codes')

        mobile = attrs.get('mobile')
        if not mobile:
            raise serializers.ValidationError('请输入手机号。')

        sms_codes = attrs.get('sms_codes')
        # 从 redis 中取出的字符串均为 Bytes，需要进行解码
        sms_codes_cache = redis_conn.get('mobile_%s' % mobile)

        if not sms_codes:
            raise serializers.ValidationError('请输入验证码')

        if not sms_codes_cache or sms_codes != sms_codes_cache.decode():
            raise serializers.ValidationError('验证已过期')

        return attrs

    def create(self, validated_data):
        """重写 create 方法，绑定用户和 openid"""

        logger.info('Enter into create function. validated_data=%s', validated_data)

        # 在 validate 校验中对于已存在的用户已添加至 validated_data 中
        user = validated_data.get('user')

        if not user:
            # 如果 validated_data 不存在 user，则重新创建用户
            keywords = {
                # 此处设置新用户的用户名为手机号，可根据业务需求随机生成用户名
                'username': validated_data.get('mobile'),
                'mobile': validated_data.get('mobile')
            }

            user = User(**keywords)

            # 设置密码
            user.set_password(validated_data.get('password'))
            user.save()

        # 绑定 user 和 openid
        OAuthQQUser.objects.create(user=user, openid=validated_data.get('openid'))

        # 返回 user（看业务需求，需要展示 user 的信息
        return user