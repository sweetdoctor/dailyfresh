from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from product.models import ProductSKU
from django_redis import get_redis_connection
from user.models import UserAddress
from django.http import JsonResponse
from order.models import OrderInfo, OrderProduct
from datetime import datetime
from django.db import transaction
from alipay import AliPay
from dailyfresh.settings import BASE_DIR


# 生成订单
@transaction.atomic
def create_order(request):
    if request.method == 'POST':
        user = request.user
        if not user.is_authenticated():
            return JsonResponse({'res': 0, 'msg': "用户未登录"})
        addr = request.POST.get('add_id')
        pay_id = request.POST.get('pay_id')
        skus = request.POST.get('skus')
        if not all([addr, pay_id, skus]):
            return JsonResponse({'res': 3, 'msg': '数据不完整'})
        # addrs = UserAddress.objects.all()
        try:
            addr = UserAddress.objects.get(id=addr)
        except UserAddress.DoesNotExist:
            return JsonResponse({'res': 1, 'msg': '地址不存在'})
        pays = OrderInfo.PAY_METHOD_DIC
        if pay_id not in pays.keys():
            return JsonResponse({'res': 2, 'msg': '不提供次收货方式'})
        # 想订单信息表中添加记录
        order_id = datetime.now().strftime('%Y%m%d%H%M%S')+str(user.id)
        transition = 10
        total_count = 0
        total_price = 0
        # 设置事务保存点
        s1 = transaction.savepoint()
        try:
            order = OrderInfo.objects.create(order_id=order_id, pay_method=pay_id, transit_price=transition,
                                     user=user,addr=addr,product_count=total_count, product_price=total_price)
            # 想订单商品表中添加数据
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            for s_id in eval(skus):
                try:
                    # s_id = int(s_id)
                    # 悲观锁处理订单并发问题。
                    p = ProductSKU.objects.select_for_update().get(id=s_id)
                except ProductSKU.DoesNotExist:
                    transaction.savepoint_rollback(s1)
                    return JsonResponse({'res': 4, 'msg': '商品不存在'})
                count = conn.hget(cart_key, s_id)
                if int(count)>p.inventory:
                    transaction.savepoint_rollback(s1)
                    return JsonResponse({'res': 6,'msg': '库存不足'})
                OrderProduct.objects.create(order_info=order, product=p, price=p.price, count=count)

                # 更新销量、库存
                p.inventory -= int(count)
                p.sales += int(count)
                p.save()

                # 累加总金额、总数量
                total_price += p.price * int(count)
                total_count += int(count)
            # 更新订单信息表中的数据
            order.product_count = total_count
            order.product_price = total_price
            order.save()
        except Exception as e:
            transaction.savepoint_rollback(s1)
            return JsonResponse({'res': 7, 'msg': '下单失败'})
        # 下订单后清除购物车数据
        conn.hdel(cart_key, *skus)
        return JsonResponse({'res': 5, 'msg': '创建成功'})


def payorder(request):
    if request.method == 'POST':
        user = request.user
        skus = request.POST.getlist('sku_id')
        print(skus)
        if not skus:
            return redirect(reverse('cart:cart'))
        conn = get_redis_connection('default')
        total_product = []
        total_price = 0
        total_count = 0
        for sku in skus:
            sku = str(sku)
            s = ProductSKU.objects.get(id=sku)
            cart_id = 'cart_%d' % user.id
            pro_count = conn.hget(cart_id, sku)
            pro_count = int(pro_count)
            pro_amount = s.price * pro_count
            s.pro_count = pro_count
            s.pro_amount = pro_amount
            total_product.append(s)
            total_count += pro_count
            total_price += pro_amount
        addrs = UserAddress.objects.filter(user=user)
        transition = 10
        total_pricewithtran = transition + total_price
        context = {
            'total_product': total_product,
            'total_price': total_price,
            'total_count': total_count,
            'transition': transition,
            'total_pricewithtran': total_pricewithtran,
            'addrs': addrs,
            'skus': skus,
        }
        return render(request, 'order/order.html', context)
    return redirect(reverse('cart:cart'))


# 生成支付链接
def orderpay(request):
    if request.method == 'POST':
        user = request.user
        if not user.is_authenticated():
            return JsonResponse({'res': 0, 'msg': '用户未登录'})

        order_id = request.POST.get('order_id')
        if not order_id:
            return JsonResponse({'res': 1, 'msg': '无效的订单号'})
        try:
            order = OrderInfo.objects.get(user=user, order_id=order_id, order_status=1, pay_method=3)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'res': 2, 'msg': '订单不存在'})
        # 调用支付宝接口
        app_private_key_string = open(BASE_DIR+'\\order\\app_private_key.pem').read()
        alipay_public_key_string = open(BASE_DIR+'\\order\\alipay_public_key.pem').read()
        # app_private_key_string == """
        #     -----BEGIN RSA PRIVATE KEY-----
        #     MIIEpAIBAAKCAQEAq1BQ0rNviAGkpdeTDOenW3Ht5nRGLnB89roS3D1oOT/YE9HAWChqYrUxY1QMs5dFouvOFkKg+2JtoxqjPiAKKHx9chahRLWSf6RhGgZ7fnJ5pQhPbnq6hkV3qf/blORLBuRdKZYbnTRL0GpbQnbTT1k5vB5kw7n2qbD3ZJhnRgbL4uqAjtwCQZngn01zu0sR4vje9bB+Wy5LM6ydgGqRzbtiHHNR3D4yFDNzdVibtETPtpr0pJ7OgVsV6xQ/dfysLJ4JFPk2OoZPGhj72EmWZm8II3mqTvbtRBPZ3NsHYnKL9gMWgMJZjlXAOYW7WQgqhfG+SupC3/YIImIMmostQwIDAQABAoIBAGY9y87EKlcoa+RSUT/NbXNE/m+gi1Yh6mKx0JnCyFYKhWHmt/2lOUDp1KzsN5xjNrsyMk/UuhDtwHMsbaqhIo7hJVkWqm7AUst9BjqrDb78gR7+Y7GS64lBIlbCDYHB8gkN94/fN2HOGUUshISZOCnOHYfpN8gcT1sc87kEv/XpE8m3l6wtj+ckMYdpvd9Frz1Y1PVUTraDSVDPHGe3EpqK+Cea3dbhnnl7HPVonJ31JagC67B7Hh869h4VP4xrx/nlEGpy7KWHxOibL/nsESZjvGzJ+wDwEHKKad5WD4wgR1n0K58XBGU22ZBAGpkub+apZ8Vqs/g9RMFwIGnXoIECgYEA4f8lrUgkVq2QSuLXifOFnaIo/z0+X5/GMhxGT2QFAMRZK/+flYuy7miAhVlr8bOMDD3r9bToImLWInSkcSiWa+vadGp90XxQcnFzRaKkqjWwSRDicSSI75h0BahCJ7+dlkjB3GTjjV2OQwcnpbvcjzBw3M+chyChlzVOoN5uXkECgYEAwg6uzg4CQ7+F0FSxNCjCk9OjfUR4ggDbav13CiW4brW9VAbUKHsyF06d3xxaS4NzBxM663ZDY40Nl3NnaS6fPKYTb5jzr53NfYQk+mi/lkhQnM/alKd7ChUjsO9yv7iCsNIFn4mETtLNdAALS8Q88BEUHGA/3kX7PncI+cwYcoMCgYEAgS0qCAX4X2MN2wAWW0/Ky/Noo5wKDvZwfywSNEbjZTDWF4QhX4VeXU92RsJ6JMmP/19VhDhHh4AfDcrGQ7gDYuSJFYnZKOh5wzB9xwvUO0Y84Ua5aBqN+wWVK7alObsZBFHKHYO9XYxgSIfKbb0XsPDrUguJWOOZ+agKrYD2bQECgYAHm1281A3ArBxJu1gq7EIcW1p4SZvTtMblHcRx0GK3bEZcqdvdLl8bTMihe1IKzb9PkrBnlH41w8y5mBuAowQ482WlpUBALRZmCi0M59hCwtjuHLO7ygjnr0Zz5B8CZvAwkDsKMvDNyjOljW7j7HBbFMBOEHPQebvMigv/BsIakwKBgQCvAzNwpHG+6XTfkTV7mJN3LCNcFw9AtSmuujPudphsWGuW3yIxP4vFKyMypYzp2nf0rTwPpOyAfHdL3tUmiQkn/sEetMlsutlgChWEMoJQ6kmDeTuyErlLhB2cTr92Z0gaEXmDgYwiaNGM9wPLQ0vfk9gTE421VifbZ4GBidJcKA==
        #     -----END RSA PRIVATE KEY-----
        # """
        #
        # alipay_public_key_string == """
        #     -----BEGIN PUBLIC KEY-----
        #     MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAoaeZ2GgnSBE2x2oDhHbaBiQNyFWradUObJwiPbk1o1xdNrbWemZ/3agHDaVLRDfcgmXQcgcwM3Y+1Pp8m4lZZgh98Wi8gR19fosblxstvSiyVrOZCCTM9FWLbR9FK8yeBsS9moyvUrABXDz3EhUubc4K4abAfCLv5UMbEKhMkdJQT8+LvyjMMI5a+ivrGruuQbUwoIgm3NVwgggLt8sg6W7vJ+33FAKzrihuw0tPAsqJq3YPxSqrCJ+m8/s1J4vAUDcSb3wblo9RaUiac2c0xwzMUrr+U58PMMVZp3pOaLIN/wrNT36upbbN12zEM6WDSqg8A6+VhzLVlPyLtmZCbwIDAQAB
        #     -----END PUBLIC KEY-----
        # """

        alipay = AliPay(
            appid="2016092300576149",
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False
        )
        total_price = order.product_price+order.transit_price
        subject = "天天生鲜{id}".format(id=order_id)

        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            # Decimal类型需要转化成字符串
            total_amount=str(total_price),
            subject=subject,
            return_url=None,
            notify_url=None  # 可选, 不填则使用默认notify url
        )
        pay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_string
        return JsonResponse({'res': 3, 'pay': pay_url})


# 查询订单状态状态
def checkorder(request):
    user = request.user
    if not user.is_authenticated():
        return JsonResponse({'res': 0, 'msg': '用户未登录'})

    order_id = request.POST.get('order_id')
    if not order_id:
        return JsonResponse({'res': 1, 'msg': '无效的订单号'})
    try:
        order = OrderInfo.objects.get(user=user, order_id=order_id, order_status=1, pay_method=3)
    except OrderInfo.DoesNotExist:
        return JsonResponse({'res': 2, 'msg': '订单不存在'})
    # 调用支付宝查询接口
    app_private_key_string = open(BASE_DIR + '\\order\\app_private_key.pem').read()
    alipay_public_key_string = open(BASE_DIR + '\\order\\alipay_public_key.pem').read()
    alipay = AliPay(
        appid="2016092300576149",
        app_notify_url=None,  # 默认回调url
        app_private_key_string=app_private_key_string,
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True  # 默认False
    )
    while True:
        response = alipay.api_alipay_trade_query(order_id)
        code = response.get('code')
        if code == '10000' and response['trade_status'] == 'TRADE_SUCCESS':
            order.trance_num = response.get('trade_no')
            order.order_status = 4
            order.save()
            return JsonResponse({'res': 3, 'msg': '支付成功'})
        elif code == '40004' or (code == '10000' and response['trade_status'] == 'WAIT_BUYER_PAY'):
            # 等待支付
            continue
        else:
            return JsonResponse({'res': 4, 'msg': '支付失败'})


