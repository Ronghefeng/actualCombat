from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^carts/v1/$', views.CartsViewV1.as_view()),
    url(r'^carts/v1/selection/$', views.CartSelectedAllVIew.as_view())
]