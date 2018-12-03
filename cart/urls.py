from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^addcart', views.add_cart, name='add_cart'),
    url(r'^updatecart', views.update_cart, name='update_cart'),
    url(r'^delete', views.delete, name='delete'),
    url(r'^$', views.cart, name='cart')
]
