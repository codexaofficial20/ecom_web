from django.contrib import admin
from .models import Category, Product, CartItem, Order, Review

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_featured', 'is_offer')
    list_editable = ('price', 'is_featured', 'is_offer')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'total_price', 'payment_method', 'delivery_date', 'is_delivered')
    list_editable = ('delivery_date', 'is_delivered')

admin.site.register(Category)
admin.site.register(Review)