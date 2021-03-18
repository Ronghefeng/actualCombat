import re

from django_redis import get_redis_connection
from rest_framework import serializers

from . import models
from meiduo.utils import auth, encryption
from celery_tasks.email import tasks


class CreateUserSerialier(serializers.ModelSerializer):
    """
    创建用户序列化类
        一、校验
            使用钩子函数做如下校验
            1、检验手机号
            2、校验验证码
            3、检查两次输入密码是否一致
            4、检查同意免责条款的值
        二、重写 create 方法
            ModelSerializer.create 会将 fields 中所有字段都存入数据库
    """

    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_codes = serializers.CharField(label='验证码', write_only=True)
    allow = serializers.CharField(label='同意免责条款', write_only=True)

    # 新增序列化字段 token，用于用户鉴权；read_only：字段只进行序列化
    token = serializers.CharField(label='token', read_only=True)

    class Meta:
        """
        1、用户注册时的所有字段：id、username、password、password2（确认密码）、mobile、sms_code、allow（是否同意免责条款）
        2、需要序列化字段（将Python对象解析为JSON）：id、username、mobile、token
        3、需要反序列化字段（将JSON解析为Python对象）：username、password、mobile、sms_code、allow
        4、模型中已存有的字段：id、username、password、mobile
        5、补充模型中除外的需要序列化的字段：password2、sms_code、allow
        6、需要存入数据库的字段：id、username、password、mobile
        7、不需要存入数据库的字段，只做反序列化操作（write_only）：password2、sms_code、allow
        8、不需要反序列化字段：password
        9、只做序列化：read_only
        """
        # 指定序列化模型
        model = models.User
        # 指定序列化字段
        fields = ['id', 'username', 'password', 'password2', 'mobile', 'sms_codes', 'allow', 'token']

        # 对字段额外修改
        extra_kwargs = {
            # 修改模型中 username 字段属性
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '用户名至少需要5位。',
                    'max_length': '用户名不能超过20位。'
                }
            },
            # 修改模型中 password 属性
            'password': {
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '密码至少需要5位。',
                    'max_length': '密码不能超过20位。'
                },
                'write_only': True  # 字段只读属性（仅进行反序列化，不进行序列化
            }
      }

    def validated_mobile(self, value):
        """检查手机号格式"""

        if not re.match(r'1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式有误。')

        return value

    def validated_allow(self, value):
        """校验是否同意免责条款的值"""

        if value == 'true':
            return value

        raise serializers.ValidationError('请先同意免责条款。')

    def validate(self, attrs):
        required_validated_fields = ['password', 'sms_codes']

        for field in required_validated_fields:
            method_name = '_validated_%s' % field
            method = getattr(self, method_name)
            attrs = method(attrs)

        return attrs

    def _validated_password(self, attrs):
        """校验密码"""

        password = attrs.get('password', None)
        password2 = attrs.get('password2', None)

        if not (password and password2) or password != password2:
            raise serializers.ValidationError('两次密码不一致。')

        return attrs

    def _validated_sms_codes(self, attrs):
        """校验验证码"""

        redis_conn = get_redis_connection('verify_codes')

        mobile = attrs.get('mobile')
        if not mobile:
            raise serializers.ValidationError('请输入手机号。')

        sms_codes = attrs.get('sms_codes')
        # 从 redis 中取出的字符串均为 Bytes，需要进行解码
        sms_codes_cache = redis_conn.get('mobile_%s' % mobile).decode()

        if not sms_codes:
            raise serializers.ValidationError('请输入验证码')

        if not sms_codes_cache or sms_codes != sms_codes_cache:
            raise serializers.ValidationError('验证已过期')

        return attrs

    def create(self, validated_data):
        unrequired_fields = ['password2', 'sms_codes', 'allow']

        # 去掉不需要存入数据库的字段
        for field in unrequired_fields:
            validated_data.pop(field)

        # 将密码取出暂存，以便之后加密后存入数据库
        password = validated_data.pop('password')

        # 创建 User 对象
        # user = User(**validated_data)
        user = models.User.objects.create_user(**validated_data)

        # 设置用户密码
        user.set_password(password)

        # 保存用户数据
        user.save()

        # 手动生成 token
        user.token = auth.generate_token(user)

        return user


class UserDetaiSerializer(serializers.ModelSerializer):
    """
    需要返回的字段：user_id、username、email、email_active、mobile
    由于字段均属于模型字段，因此可以直接继承 ModelSerializer
    """
    class Meta:
        model = models.User
        fields = ['id', 'username', 'email', 'email_active', 'mobile']


class EmailSerializer(serializers.ModelSerializer):
    """
    由于 email 字段在模型中存在，且需要进行反序列化和序列化操作，因此选择 ModelSerializer
    """
    class Meta:
        model = models.User
        fields = ['id', 'email']

        extra_kwargs = {
            # 由于 email 字段在 Django 原生模型中为 EmailField 字段，且允许为空，此序列化器用于修改邮箱场景，
            # 因此需要修改其默认属性，不允许为空
            # EmailField 对自动检验该字段值的合法性
            'email': {
                'required': True
            }
        }

    def update(self, instance, validated_data):
        """
        instance: User 对象
        validated_data：反序列化后的数据
        因当前业务需求需要支持设置邮箱时，发送邮箱激活邮件，因此重写 update 方法
        """
        # 更新邮箱
        instance.email = validated_data.get('email')
        instance.save()

        email_params = {
            'subject': '美多用户激活邮箱',
            'to_email': instance.email,
            'verify_url': encryption.generate_email_verify_url(instance) # 激活链接
        }
        # 使用 celery 异步发送邮件
        tasks.send_verify_email.delay(**email_params)

        return instance

