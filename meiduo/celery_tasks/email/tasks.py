import logging

from django.conf import settings
from django.core.mail import send_mail

from celery_tasks.main import celery_app


logger = logging.getLogger('django')


@celery_app.task(name='send_verify_email')
def send_verify_email(subject, to_email, verify_url):
    """
    发送邮件
    subject：邮件主题
    to_email：收件人邮件地址
    verify_url：激活链接
    """

    # 因为邮件正文中含有超链接，因此使用 html_message，而不是 message
    html_message = '<p>尊敬的用户您好！' \
                   '</p><p>感谢您使用美多商城。</p><p>您的邮箱为：%s，' \
                   '请点击此链接激活您的邮箱：</p><p><a href="%s">%s<a></p>'\
                   % (to_email, verify_url, verify_url)

    keywords = {
        'subject': subject,
        # message 必须指定，但当前业务需要超链接，因此不使用，置为空即可
        'message': '',
        'html_message': html_message,
        'from_email': settings.EMAIL_HOST_USER,
        # 收件人，列表类型
        'recipient_list': [to_email]
    }

    send_mail(**keywords)

    logger.info('邮件已发送。keywords=%s', keywords)