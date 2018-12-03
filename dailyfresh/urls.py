from django.conf.urls import url, include
from django.contrib import admin
from product.views import home
from dailyfresh.settings import BASE_DIR
from django.shortcuts import render


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^search/', include('haystack.urls')),
    url(r'^user/', include('user.urls', namespace='user')),
    url(r'^order/', include('order.urls', namespace='order')),
    url(r'^cart/', include('cart.urls', namespace='cart')),
    url(r'^product/', include('product.urls', namespace='product')),
    url(r'^$', home, name='home'),
]
