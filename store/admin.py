from django.contrib import admin
from .models import Item, Discount, Tax, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Инлайн для отображения товаров в заказе в админке"""
    model = OrderItem
    extra = 1
    min_num = 1


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """Админка для модели Item"""
    list_display = ('name', 'price', 'currency', 'get_display_price')
    list_filter = ('currency',)
    search_fields = ('name', 'description')


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    """Админка для модели Discount"""
    list_display = ('name', 'percent_off')


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    """Админка для модели Tax"""
    list_display = ('name', 'percent')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Админка для модели Order с возможностью просмотра и редактирования позиций заказа"""
    list_display = ('id', 'created_at', 'get_total_price', 'get_currency')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'updated_at')
