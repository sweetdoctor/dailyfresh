from django.shortcuts import render, HttpResponse
from .models import ProductCategory, ProductBanner, PromotionPc, TypeShow, Products
from django_redis import get_redis_connection
from django.core.cache import cache
from product.models import ProductSKU
from django.core.paginator import Paginator, EmptyPage
from django.core.urlresolvers import reverse
from django.http import JsonResponse

def home(request):
    context = cache.get('index_page_cache')
    if context is None:
        print('没有缓存')
        types = ProductCategory.objects.all()
        banners = ProductBanner.objects.all().order_by('index')
        promotion = PromotionPc.objects.all().order_by('index')
        for type in types:
            word_show = TypeShow.objects.filter(product_type=type, display_type=0).order_by('index')
            pic_show = TypeShow.objects.filter(product_type=type, display_type=1).order_by('index')
            type.word_show = word_show
            type.pic_show = pic_show
        context = {
                'types': types,
                'banners': banners,
                'promotion': promotion,
            }
        # 设置缓存
        cache.set('index_page_cache', context)
    user = request.user
    if user.is_authenticated():
        cart_key = 'cart_%d' % user.id
        con = get_redis_connection('default')
        cart_count = con.hlen(cart_key)
        context['cart_count'] = cart_count
    return render(request, 'products/home.html', context)


def detail(request, sku_id):
    types = ProductCategory.objects.all()
    try:
        product = ProductSKU.objects.get(id=sku_id)
    except ProductSKU.DoesNotExist:
        return HttpResponse('访问页面不存在')
    new_products = ProductSKU.objects.filter(type=product.type).order_by('-update_date')[:2]
    same_spu_products = ProductSKU.objects.filter(products=product.products).exclude(id=sku_id)
    context = {
        'product': product,
        'types': types,
        'new_products': new_products,
        'same_spu_products': same_spu_products,
    }
    user = request.user
    if user.is_authenticated():
        cart_key = 'cart_%d' % user.id
        history_key = 'history_%user' % user.id
        con = get_redis_connection('default')
        con.lrem(history_key, 0, sku_id)
        con.lpush(history_key, sku_id)
        con.ltrim(history_key, 0, 4)
        cart_count = con.hlen(cart_key)
        context['cart_count'] = cart_count
    return render(request, 'products/detail.html', context)


def list(request, type, page_num):
    user = request.user
    sort = request.GET.get('sort', 'default')
    try:
        page_num = int(page_num)
    except Exception:
        page_num = 1
    types = ProductCategory.objects.all()
    type = ProductCategory.objects.get(id=type)
    if sort == 'price':
        skus = ProductSKU.objects.filter(type=type).order_by('price')
    elif sort == 'sales':
        skus = ProductSKU.objects.filter(type=type).order_by('-sales')
    else:
        skus = ProductSKU.objects.filter(type=type)

    page_manage = Paginator(skus, 1)

    try:
        page = page_manage.page(page_num)
    except EmptyPage:
        page = page_manage.page(1)
    new_products = ProductSKU.objects.filter(type=type).order_by('-update_date')[:2]
    # 控制页码显示5页
    total_page_num = page_manage.num_pages
    if total_page_num<5:
        show_nums = range(1, total_page_num+1)
    elif page_num<=3:
        show_nums = range(1,6)
    elif total_page_num-page_num <= 2:
        show_nums = range(page_num-4, total_page_num+1)
    else:
        show_nums = range(page_num-2, page_num+3)
    # show_nums = range(10)
    if user.is_authenticated():
        cart_key = 'cart_%d' % user.id
        con = get_redis_connection('default')
        cart_count = con.hlen(cart_key)
    else:
        cart_count = 0
    context = {
        'types': types,
        'page': page,
        'new_products': new_products,
        'current_type': type,
        'sort': sort,
        'show_nums': show_nums,
        'cart_count': cart_count,
    }
    return render(request, 'products/list.html', context)



