from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'index/$', views.home, name='home'),
    url(r'detail/(?P<sku_id>\d+)$', views.detail, name='detail'),
    url(r'list/(?P<type>\d+)/(?P<page_num>\d+)/$', views.list, name='list'),
    # url(r'$', views.home, name='home'),
]
