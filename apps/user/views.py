from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from itsdangerous import TimedJSONWebSignatureSerializer as Se
from itsdangerous import SignatureExpired
from django.conf import settings
from apps.user.models import User
from celery_tasks.tasks import send_email_task
from django.contrib.auth.decorators import login_required
import re
# Create your views here.


# 创建视图类，来处理注册视图 /register
class RegisterView(View):
    """注册"""

    def get(self, request):
        """get请求，显示页面"""
        print("get")
        return render(request, "user/register.html")

    def post(self, request):
        """post请求，提交数据，进行注册"""
        # 1.接收参数
        print("post")
        username = request.POST.get("user_name")
        password = request.POST.get("pwd")
        email = request.POST.get("email")

        # 2.校验参数
        # 校验参数是否完整
        if not all([username, password, email]):
            # 如果all()返回False, 代表至少一项为空，则返回
            error_msg = "请填写正确的信息"
            return render(request, "user/register.html", {'error_msg': error_msg})

        # 校验用户名是否已经存在
        if User.objects.filter(username=username):
            # 返回True，代表用户名存在
            error_msg = "用户名已经存在"
            return render(request, "user/register.html", {'error_msg': error_msg})

        # 校验邮箱格式是否正确
        if not re.match(r"^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$", email):
            error_msg = "邮箱格式不正确"
            return render(request, "user/register.html", {"error_msg": error_msg})

        # 校验邮箱是否已被注册过
        # if User.objects.filter(email=email):
        #     # 返回True，代表用户名存在
        #     error_msg = "该邮箱已被注册过"
        #     return render(request, "user/register.html", {'error_msg': error_msg})

        # 3.业务处理：校验通过，注册帐号
        user = User.objects.create_user(username=username, password=password, email=email)
        # 更改为未激活状态
        user.is_active = 0
        user.save()
        # 注册后需向用户发送邮件进行激活
        # 邮件点击激活的网址格式为：/user/active/user_id,需进行加密，用itsdangerous模块
        # 获取对象,进行加密
        se = Se(settings.SECRET_KEY, 1800)  # 密钥使用django默认，过期时间30min
        info = {"confirm": user.id}
        # 对用户信息加密，返回的是byte类型数据，解码转换为str
        token = se.dumps(info).decode()
        # 把token信息发送到用户邮箱  该处发邮件需用网络，存在网络延迟等影响用户体验的问题，可以用celery解决
        '''# 邮件主题
        subject = "注册激活"
        # 接收邮箱
        email_list = [email]
        html_msg = """<h1>%s，恭喜您注册成为天天生鲜会员，请点击链接进行激活，30分钟后链接失效</h1>
        <a href="http://192.168.137.129:9999/user/active/%s">http://192.168.137.129:9999/user/active/%s</a>
                    """ % (username, token, token)

        send_mail(subject=subject, message="", from_email=settings.EMAIL_FROM, recipient_list=email_list, html_message=html_msg)
        '''
        # 利用celery发送激活邮件
        print("发送激活邮件")
        send_email_task.delay(email, username, token)

        # 4.返回应答
        return redirect(reverse("goods:index"))


# 注册激活 /user/active/token信息
class ActiveView(View):
    """激活页面"""
    def get(self, request, token):
        se = Se(settings.SECRET_KEY, 1800)  # 密钥使用django默认，过期时间30min
        # 对token信息进行解密
        try:
            info = se.loads(token)
            # 获取用户id
            user_id = info["confirm"]
            user = User.objects.get(id=user_id)
            # 更改为已激活
            user.is_active = 1
            user.save()

            # 跳转到登录页面
            return redirect(reverse("user:login"))
        except SignatureExpired:
            """返回信息说明"""
            return HttpResponse("链接已失效")


# /login 登录
class LoginView(View):
    """登录页面"""
    def get(self, request):
        """显示登录页面"""
        # 判断是否设置cookie
        if "username" in request.COOKIES:
            # 如果设置了，则显示用户名，并勾选记住用户名
            username = request.COOKIES["username"]
            checked = "checked"
        else:
            # 如果没有设置cookie，则不显示
            username = ""
            checked = ""

        return render(request, 'user/login.html', {"username": username, "checked": checked})

    def post(self, request):
        """登录处理"""
        # 1.获取数据
        username = request.POST.get("username")
        password = request.POST.get("pwd")
        remember = request.POST.get("remember")
        # 2.校验数据
        # 校验数据完整性
        if not all([username, password]):
            # 数据不完整，返回重新登录
            error_msg = "请输入用户名或密码"
            return render(request, "user/login.html", {"error_msg": error_msg})
        # 校验用户名与密码是否匹配，用user自带方法 authenticate()
        # 如果匹配成功，该方法返回User对象，否则 返回None
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                # 代表用户已激活
                # 记住用户登录状态，会自动设置用户session
                login(request, user)
                # 跳转到首页
                response = redirect(reverse("user:index"))
                # 判断是否勾选记住用户名
                if remember == "on":
                    # 记住用户名，设置cookie
                    response.set_cookie("username", username)
                else:
                    # 未勾选记住用户名，清除cookie
                    response.delete_cookie("username")
                # 跳转页面
                return response
            else:
                error_msg = "用户未激活，请激活"
                return render(request, "user/login.html", {"error_msg": error_msg})
        # 匹配不成功，表示用户名或密码错误
        error_msg = "用户名或密码错误"
        return render(request, "user/login.html", {"error_msg": error_msg})


# /logout 退出
class LogoutView(View):
    """退出"""
    def get(self, request):
        # 退出，清除用户信息
        logout(request)
        # 跳转到登录页面
        return redirect(reverse("user:login"))


# /user_info 用户中心
class UserInfoView(View):
    """用户信息中心"""
    def get(self, request):

        return render(request, "user/user_center_info.html")


# /user_order 用户中心订单
class UserOrderView(View):
    """用户订单"""
    def get(self, request):

        return render(request, "user/user_center_order.html")


# /user_site 用户收货地址
class UserSiteView(View):
    """用户订单"""

    def get(self, request):
        return render(request, "user/user_center_site.html")






