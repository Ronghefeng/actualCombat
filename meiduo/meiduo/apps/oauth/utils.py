# QQ 登录
import logging
import requests

from urllib.parse import urlencode, parse_qs

from . import constants


logger = logging.getLogger('django')


class OAuthQQ:

    def __init__(self, client_id=None, client_secret=None, redirect_url=None, state=next):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_url = redirect_url
        # 用于保存登录成功后的跳转路径
        self.state = state

    def get_authorization_code_url(self):
        """QQ 登录参数组建"""

        data_dict = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_url,
            'state': self.state
        }

        # urlencode(data_dict) 会将 data_dict 的 key-value 拼接为 url 请求参数
        return constants.QQ_AUTHORIZATION_CODE_URL + urlencode(data_dict)

    def get_access_token(self, code):
        """
        拼接 Access Token 的 url
        请求 QQ 服务器，获取 Access Toke
        """
        data_dict = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_url': self.redirect_url
        }

        url =  constants.QQ_ACCESS_TOKEN_URL + urlencode(data_dict)

        try:
            # 后端请求 QQ 服务器
            response = requests.get(url)
        except Exception as e:
            logger.error('请求 QQ 服务获取 Access Token 失败，错误信息：%s' % e)
            raise Exception('请求 QQ 服务获取 Access Token 失败。')

        # 提取响应数据，转化为字典
        ret_data = parse_qs(response.text)

        access_token = ret_data.get('access_token', None)

        if not access_token:
            raise Exception('获取 Access Token 失败。')

        return access_token[0]

    def get_openid(self, access_token):

        url = constants.QQ_USER_OPENID_URL + 'access_token=%s/' % access_token

        try:
            # 后端请求 QQ 服务器
            response = requests.get(url)
        except Exception as e:
            logger.error('请求 QQ 服务获取 openid 失败，错误信息：%s' % e)
            raise Exception('请求 QQ 服务获取 openid 失败。')

        # 提取返回数据
        ret_data = parse_qs(response.text)

        if not ('openid' in ret_data and 'client_id' in ret_data):
            raise Exception('请求 QQ 服务获取 openid 失败。')

        return ret_data


