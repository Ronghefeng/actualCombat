from django.urls import path, re_path
from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCode.as_view()),
    url(r'^sms_codes/', views.test)
]