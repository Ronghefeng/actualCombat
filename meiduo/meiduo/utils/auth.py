# 用户状态保持
from rest_framework_jwt.settings import api_settings


def generate_token(user):
    """
    生成用户的 token，用于 JWT 鉴权
    """

    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)

    return token

