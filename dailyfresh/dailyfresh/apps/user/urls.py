from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from . import views


urlpatterns = [
    url(r'^register$', views.RegisterView.as_view(), name='register'),  # 注册
    url(r'^active/(\S+)$', views.ActiveView.as_view(), name='active'),  # 激活
    url(r'^login$', views.LoginView.as_view(), name='login'),  # 登录页面
    url(r'^logout$', views.LogoutView.as_view(), name='logout'),  # 退出处理
    url(r'^user_info$', login_required(views.UserInfoView.as_view()), name='user_info'),  # 用户中心，登录后才能进去
    url(r'^user_order$', login_required(views.UserOrderView.as_view()), name='user_order'),  # 用户订单，登录后才能进去
    url(r'^user_site$', login_required(views.UserSiteView.as_view()), name='user_site'),  # 用户收货地址，登录后才能进去


]
