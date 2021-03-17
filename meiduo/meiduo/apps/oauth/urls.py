from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^qq_oauth_url/$', views.QQOAuthURLView.as_view()),
    url(r'^qq_oauth/$', views.QQOAuthView.as_view())
]
