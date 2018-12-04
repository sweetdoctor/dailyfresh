from django.shortcuts import render
from django.http import JsonResponse
from django_redis import get_redis_connection
from django.contrib.auth.decorators import login_required
from product.models import ProductSKU


@login_required
def cart(request):
    user = request.user
    conn = get_redis_connection('default')
    cart_key = 'cart_%d' % user.id
    carts = conn.hgetall(cart_key)
    total_count = 0
    cart_products = []
    for sku_id, key in carts.items():
        total_count += int(key)
        p = ProductSKU.objects.get(id=sku_id)
        p.count = int(key)
        p.product_total_price = float(p.price)*int(key)
        cart_products.append(p)
    return render(request, 'cart/cart.html', {'carts': cart_products, 'total_count': total_count})


def add_cart(request):
    user = request.user
    if request.method == "POST":
        if not user.is_authenticated():
            return JsonResponse({'status': 0, 'msg': '您还没有登录'})
        sku_id = request.POST['sku_id']
        count = request.POST['count']
        print(sku_id, count)
        if not all([sku_id, count]):
            return JsonResponse({'status': 1, 'msg': '数据不完整'})
        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'status': 2,'msg': '商品数目出错'})
        try:
            product = ProductSKU.objects.get(id=sku_id)
        except ProductSKU.DoesNotExist:
            return JsonResponse({'status': 3, 'msg': '商品不存在'})
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        try:
            db_count = conn.hget(cart_key, sku_id)
            db_count += count
        except Exception:
            db_count = count
        conn.hset(cart_key, sku_id, db_count)
        total_count = conn.hlen(cart_key)
        return JsonResponse({'status': 5, 'msg': '添加成功', 'total_count': total_count})


def update_cart(request):
    user = request.user
    if request.method == "POST":
        if not user.is_authenticated():
            return JsonResponse({'status': 0, 'msg': '您还没有登录'})
        sku_id = request.POST['sku_id']
        count = request.POST['count']
        print(sku_id, count)
        if not all([sku_id, count]):
            return JsonResponse({'status': 1, 'msg': '数据不完整'})
        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'status': 2, 'msg': '商品数目出错'})
        try:
            product = ProductSKU.objects.get(id=sku_id)
        except ProductSKU.DoesNotExist:
            return JsonResponse({'status': 3, 'msg': '商品不存在'})
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        try:
            db_count = conn.hget(cart_key, sku_id)
            db_count += count
        except Exception:
            db_count = count
        if db_count>product.inventory:
            return JsonResponse({'status': 6, 'msg': '库存不足'})
        conn.hset(cart_key, sku_id, db_count)
        num = 0
        for value in conn.hgetall(cart_key).values():
            num += int(value)
        return JsonResponse({'status': 5, 'msg': '添加成功', 'total_count': db_count})


def delete(request):
    if request.method == "POST":
        user = request.user
        if not user.is_authenticated():
            return JsonResponse({'status': 0, 'msg': '您还没有登录'})
        sku_id = request.POST['sku_id']
        if not sku_id:
            return JsonResponse({'status': 1, 'msg': '商品为空'})
        try:
            sku_id = int(sku_id)
            product = ProductSKU.objects.get(id=sku_id)
        except ProductSKU.DoesNotExist:
            return JsonResponse({'status': 2, 'msg': '商品不存在'})
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        conn.hdel(cart_key, sku_id)
        count1 = 0
        for count in conn.hgetall(cart_key).values():
            count = int(count)
            count1 += count
        return JsonResponse({'status': 3, 'msg': '删除成功', 'count': count1})
