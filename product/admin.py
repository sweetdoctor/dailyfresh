from django.contrib import admin
from .models import ProductCategory, ProductSKU, ProductBanner, PromotionPc, TypeShow, Products
from django.core.cache import cache


class BaseAdmin(admin.ModelAdmin):
    # 更新数据后应该执行删除缓存操作
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.delete('index_page_cache')
    # 删除数据执行删除缓存
    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        cache.delete('index_page_cache')


class TypeShowAdmin(BaseAdmin):
    list_display = ('product_type', 'display_type', 'product',)


class ProductCategoryAdmin(BaseAdmin):
    pass


class ProductBannerAdmin(BaseAdmin):
    pass


class ProductPromotionAdmin(BaseAdmin):
    pass


admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(ProductSKU)
admin.site.register(ProductBanner, ProductBannerAdmin)
admin.site.register(PromotionPc, ProductPromotionAdmin)
admin.site.register(TypeShow, TypeShowAdmin)
admin.site.register(Products)
