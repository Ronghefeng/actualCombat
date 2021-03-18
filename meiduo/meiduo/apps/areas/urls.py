from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from . import views


urlpatterns = [
    url(r'^areas/v1/$', views.AreaListViewV1.as_view()),
    url(r'area/(?P<pk>\d+)/v1/$', views.AreaDetailViewV1.as_view()),
    url(r'^areas/v2/$', views.AreaListViewV2.as_view()),
    url(r'area/(?P<pk>\d+)/v2/$', views.AreaDetailViewV2.as_view()),
]

# DefaultRouter 与 SimpleRouter 区别，SimpleRouter 不会自动带上根目录
router = DefaultRouter()
# basename：在视图中如果有指定 queryset 属性时，不设置的情况下，会自动取 queryset 的模型名小写
router.register(r'areas', views.AreaViewSet, basename='area')

urlpatterns += router.urls