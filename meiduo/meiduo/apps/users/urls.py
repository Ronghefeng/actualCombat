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
    url(r'^authorizations/$', obtain_jwt_token),

    # 获取用户详情信息，按照 restful 规范，路径资源名应该为复数，但该路选择使用单数，原因：
    # 1、使用复数同上述路径重合，无法到达
    # 2、规范中获取单条数据需要提供 pk，但是在此视图实现逻辑中，考虑到减少数据库查询提高性能，
    # 未使用 pk 作为过滤条件，因此路径中无需提供 pk 关键字
    url(r'^user/$', views.UserDetailView.as_view()),

    # 更新邮箱
    url(r'email/$', views.EmailView.as_view()),
    # 激活邮箱
    url(r'^email/verify/$', views.EmailVerifyView.as_view())
]