from django.contrib import admin
from .models import Category, Product, ProductImages

class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'product_image', 'price', 'category', 'in_stock']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'category_image']

class ProductImagesAdmin(admin.ModelAdmin):
    list_display = ['product', 'product_image', 'date']

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ProductImages, ProductImagesAdmin)
