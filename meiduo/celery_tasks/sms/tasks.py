from celery_tasks.main import celery_app
from . import constants
from .yuntongxun.sms import CCP


# @celery_app.task 注册该任务
# name：自定义任务名
@celery_app.task(name='send_sms_codes')
def send_sms_codes(mobile, sms_codes):
    """
    定义发送短信的任务
    """
    ccp = CCP()
    ccp.send_template_sms(mobile, [sms_codes, constants.SMS_CODES_EXPIRE_TIME // 60], constants.CCP_TEMPLATE)
