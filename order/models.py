from django.db import models
from db.base_model import BaseModel


class OrderInfo(BaseModel):
    PAY_METHOD = (
        (1, '货到付款'),
        (2, '微信支付'),
        (3, '支付宝'),
        (4, '银联支付')
    )
    PAY_METHOD_DIC = {
        '1': '货到付款',
        '2': '微信支付',
        '3': '支付宝',
        '4': '银联支付'
    }
    ORDER_status = (
        (1, '待支付'),
        (2, '代发货'),
        (3, '待收货'),
        (4, '待评价'),
        (5, '已完成'),
    )
    ORDER_status_dic = {
        '1': '待支付',
        '2': '代发货',
        '3': '待收货',
        '4': '待评价',
        '5': '已完成',
    }

    order_id = models.CharField(max_length=100, verbose_name='订单编号')
    pay_method = models.SmallIntegerField(choices=PAY_METHOD, default=3, verbose_name='支付方式')
    order_status = models.SmallIntegerField(choices=ORDER_status, default=1, verbose_name='订单状态')
    product_count = models.IntegerField(verbose_name='产品数量')
    product_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='总价格')
    transit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='运费')
    user = models.ForeignKey('user.User', verbose_name='用户')
    addr = models.ForeignKey('user.UserAddress', verbose_name='地址')
    trance_num = models.CharField(max_length=100, default='', verbose_name='支付编号')

    class Meta:
        db_table = 'order_info'
        verbose_name = '订单信息'
        verbose_name_plural = verbose_name


class OrderProduct(BaseModel):
    count = models.SmallIntegerField(default=1, verbose_name='商品数目')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品价格')
    product = models.ForeignKey('product.ProductSKU', verbose_name='商品SKU')
    order_info = models.ForeignKey(OrderInfo, verbose_name='订单信息')
    comment = models.CharField(max_length=128, default='', verbose_name='评论')

    class Meta:
        db_table = 'product_order'
        verbose_name = '商品订单'
        verbose_name_plural = verbose_name