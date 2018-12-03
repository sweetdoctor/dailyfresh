from __future__ import absolute_import, unicode_literals
from celery import shared_task
from product.models import ProductCategory, PromotionPc, ProductBanner, TypeShow
from django.template import loader
from dailyfresh.settings import BASE_DIR
import os


@shared_task
def generate_static_index_html():
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
    template_html = loader.get_template('template_static_index_html.html')
    html = template_html.render(context)
    # save_path = os.path.join('D:/pythonproject/dailyfresh'+'/static/static_index_html.html')
    with open('static.html', 'w', encoding='utf-8') as f:
        f.write(html)
