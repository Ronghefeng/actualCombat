from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^orders/settelment/$', views.OrderSettlementView.as_view()),
    url(r'^orders/$', views.CommitOrderView.as_view())
]