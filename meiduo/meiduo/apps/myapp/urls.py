from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^article/$', views.ArticleView.as_view())
]