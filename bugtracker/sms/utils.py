from django.conf import settings

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


client = AcsClient(
    settings.ALIYUN_ACCESSKEYID,
    settings.ALIYUN_ACCESSSECRET,
    'cn-qingdao')

request = CommonRequest()
request.set_accept_format('json')
request.set_domain('dysmsapi.aliyuncs.com')
request.set_method('POST')
request.set_protocol_type('https')  # https | http
request.set_version('2017-05-25')
request.set_action_name('SendSms')

response = client.do_action(request)

