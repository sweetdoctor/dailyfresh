from django.shortcuts import render, HttpResponse, redirect
from user.models import User
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from user.models import UserAddress
from django_redis import get_redis_connection
from product.models import ProductSKU
from .tasks import send_register_email
from order.models import OrderInfo, OrderProduct
from django.core.paginator import Paginator, EmptyPage


def register(request):
    # get请求返回注册页面，post请求进行注册
    if request.method == "POST":
        # 获取提交过来的数据
        username = request.POST['user_name']
        pwd = request.POST['pwd']
        email = request.POST['email']
        # create_user()方法会对密码进行hash
        user = User.objects.create_user(username, email, pwd)
        # 账户的激活状态为0表示未激活
        user.is_active = 0
        user.save()
        # 发送激活链接，生成加密的token
        active_id = {'confirm': username}
        token = Serializer(settings.SECRET_KEY, 3600).dumps(active_id)
        # print(type(token))
        token = str(token, encoding='utf-8')
        # 将任务发送到Redis消息队列中，异步执行
        send_register_email.delay(username, token, email)
        return redirect(reverse('product:home'))
    return render(request, 'user/register.html')


def active_acount(request, token):
    print(token)
    # return HttpResponse('return HttpResponse(eyJhbGciOiJIUzUxMiIsImlhdCI6MTU0MzIyMzk4OCwiZXhwIjoxNTQzMjI3NTg4fQ.eyJjb25maXJtIjoiZG9jdG9yMjEifQ.vd3IN96DrSUCis2adjWmHkRrk-pxqb9sYHLsTEBFNMxzfHr2qXVU1BCnSwVEj11t85gIMMFSK3vUpqk3FLpGlw)')
    s = Serializer(settings.SECRET_KEY, 3600)
    try:
        active_id = s.loads(bytes(token, encoding='utf-8'))
    except SignatureExpired as e:
        return HttpResponse('激活链接已过期')
    except Exception:
        return HttpResponse('激活链接无效')
    username = active_id['confirm']
    user = User.objects.get(username=username)
    user.is_active = 1
    user.save()
    return HttpResponse(token)


def check_name(request, name):
    # 尝试从数据库查找该用户名是否存在，如果有返回0，否则返回1
    try:
        user = User.objects.get(username=name)
    except Exception as e:
        user = None
    if user:
        flag = 0
    else:
        flag = 1
    return HttpResponse(flag)


def tt_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['pwd']
        # 获取复选框value值，以列表的形式，没有选中value值为空
        remember = request.POST.getlist('remember')
        next_url = request.GET.get('next', reverse('product:home'))
        # 密文验证
        user = authenticate(username=username, password=password)
        if user is not None:
            if not user.is_active:
                return render(request, 'user/register_active.html')
            else:
                # 记录用户登录状态
                login(request, user)
                response = redirect(next_url)
                if len(remember)==1:
                    response.set_cookie('name', username, max_age=7*24*3600)
                else:
                    response.delete_cookie('name')
            return response
        else:
            return render(request, 'user/login.html', {'error': '用户名或者密码错误'})
    if 'name' in request.COOKIES:
        username = request.COOKIES.get('name', 0)
    else:
        username = ''
    return render(request, 'user/login.html', {'username': username})


def user_logout(request):
    logout(request)
    return redirect(reverse('product:home'))


@login_required
def user_info(request):
    user = request.user
    # 自定义管理类，并封装get_default_addr方法
    address = UserAddress.objects.get_default_addr(user)
    # 获取用户浏览记录
    con = get_redis_connection('default')
    history_key = 'history_%user'%user.id
    history_ids = con.lrange(history_key, 0, 4)
    product_list = []
    for p_id in history_ids:
        product = ProductSKU.objects.get(id=p_id)
        product_list.append(product)

    return render(request, 'user/user_center_info.html', {'address': address,
                                                          'product_list': product_list})

@login_required
def useraddress(request):
    user = request.user
    if request.method == 'POST':
        recipient = request.POST['recipient']
        address = request.POST['address']
        try:
            zip_code = int(request.POST['zip_code'])
        except Exception:
            pass
        phone = request.POST['phone']
        default_addr = UserAddress.objects.get_default_addr(user)
        if default_addr:
            is_default = False
        else:
            is_default = True
        UserAddress.objects.create(recipient=recipient, address=address, zip_code=zip_code, contact_num=phone, is_default=is_default, user=user)
        return redirect('user:useraddress')
    address = UserAddress.objects.get_default_addr(user)
    return render(request, 'user/user_address.html', {'address': address})


@login_required
def user_order(request, page_num):
    user = request.user
    page_num = int(page_num)
    orders = OrderInfo.objects.filter(user=user).order_by('-create_date')
    ord_status = OrderInfo.ORDER_status_dic
    for o in orders:
        ps = OrderProduct.objects.filter(order_info=o)
        for amount in ps:
            # 动态为每个订单提供小计
            total = amount.price * amount.count
            amount.total = total
        # 动态为每个订单提供订单下所有商品信息
        o.ps = ps
        # 获取订单的状态
        o.status = ord_status[str(o.order_status)]
    # 使用Django内置分页，每页显示1个订单
    page_manage = Paginator(orders, 1)
    try:
        # 创建Page对象，如果页面取不到，得到第一个页面page对象
        page = page_manage.page(page_num)
    except EmptyPage:
        page = page_manage.page(1)
    # 控制页码显示5页
    total_page_num = page_manage.num_pages
    if total_page_num < 5:
        show_nums = range(1, total_page_num + 1)
    elif page_num <= 3:
        show_nums = range(1, 6)
    elif total_page_num - page_num <= 2:
        show_nums = range(page_num - 4, total_page_num + 1)
    else:
        show_nums = range(page_num - 2, page_num + 3)

    context = {
        'orders': orders,
        'page': page,
        'show_nums': show_nums,
    }
    return render(request, 'user/user_order.html', context)
