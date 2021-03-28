"""meiduo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('verifications.urls')),   # 短信验证码模块
    path('', include('users.urls')),   # 用户模块
    path('', include('oauth.urls')),
    path('', include('areas.urls')),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),  # 富文本编辑器路由，固定配置
    path('', include('contents.urls')),
    url(r'^', include('goods.urls')),
    url(r'^', include('cards.urls')),
    url(r'^', include('orders.urls')),
    url(r'^', include('myapp.urls'))
]
