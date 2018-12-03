from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^register/checkname/(?P<name>\w+)$', views.check_name, name='checkname'),
    url(r'^register/active/(?P<token>.*)$', views.active_acount, name='active'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.tt_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^userinfo/$', views.user_info, name='userinfo'),
    url(r'^userorder/(\w+)$', views.user_order, name='userorder'),
    url(r'^useraddress', views.useraddress, name='useraddress'),
    # url(r'^useraddress', views.useraddress, name='useraddress'),
]
