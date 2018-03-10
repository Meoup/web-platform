from celery import Celery
from django.core.mail import send_mail
from django.conf import settings
import os

# 初始化django环境变量
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
# 创建Celery对象
app = Celery("send_email_task", broker="redis://127.0.0.1:6379/2")


# 封装任务函数
@app.task
def send_email_task(email, username, token):
    # 邮件主题
    subject = "注册激活"
    # 接收邮箱
    email_list = [email]
    html_msg = """
            <h1>%s，恭喜您注册成为天天生鲜会员，请点击链接进行激活，30分钟后链接失效</h1>
            <a href="http://192.168.137.129:9999/user/active/%s">http://192.168.137.129:9999/user/active/%s</a>
            """ % (username, token, token)

    send_mail(subject=subject, message="", from_email=settings.EMAIL_FROM,
              recipient_list=email_list, html_message=html_msg)
