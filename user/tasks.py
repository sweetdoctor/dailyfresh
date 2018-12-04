from __future__ import absolute_import, unicode_literals
from celery import shared_task
from dailyfresh import settings
from django.core.mail import send_mail

@shared_task
def send_register_email(username, token, email):
    message = ''
    title = '天天生鲜欢迎信息'
    body = '<h1>{name}，欢迎成为天天生鲜会员</h1>请点击下面链接激活账号<a href="http://127.0.0.1:8000/user/register/active/{token}">http://127.0.0.1:8000/user/register/active/{token}</a>'.format(
        name=username, token=token)
    try:
        send_mail(title, message, settings.EMAIL_FROM, [email], html_message=body)
    except Exception as e:
        pass
