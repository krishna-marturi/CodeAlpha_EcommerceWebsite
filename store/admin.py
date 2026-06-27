from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'price', 'quantity', 'subtotal')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'sale_price', 'stock', 'featured', 'active', 'created_at')
    list_filter = ('category', 'featured', 'active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('price', 'sale_price', 'stock', 'featured', 'active')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 'first_name', 'last_name', 'city', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'first_name', 'last_name', 'email')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at', 'total_price')
    inlines = [OrderItemInline]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'item_count', 'total', 'created_at')
    list_filter = ('created_at',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('user__username', 'product__name')


# Customize admin site header
admin.site.site_header = 'ShopZen Admin'
admin.site.site_title = 'ShopZen'
admin.site.index_title = 'Welcome to ShopZen Administration'
