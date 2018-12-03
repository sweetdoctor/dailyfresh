from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^commit/$', views.create_order, name='corder'),
    url(r'^payorder/$', views.payorder, name='payorder'),
    url(r'^orderpay/$', views.orderpay, name='orderpay'),
    url(r'^checkorder/$', views.checkorder, name='checkorder'),
]
