from django.urls import path
from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from . import views

urlpatterns = [
    # 用户注册
    url(r'^users/$', views.UserView.as_view()),
    # 用户名校验
    url(r'^users/(?P<username>\w{5,20})/count/$', views.UsernameCheckView.as_view()),
    # 手机校验
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCheckView.as_view()),
    # JWT 登录，根据用户名和密码登录，然后生成 token 返回
    url(r'^authorizations/$', obtain_jwt_token)
]