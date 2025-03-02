from django.contrib import admin
from .models import Item, Discount, Tax, Order, OrderItem
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet


class OrderItemInlineFormSet(BaseInlineFormSet):
    """Формсет для валидации, что все товары в заказе имеют одинаковую валюту"""
    def clean(self):
        super().clean()
        currencies = set()
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                item = form.cleaned_data.get('item')
                if item:
                    currencies.add(item.currency)

        if len(currencies) > 1:
            raise ValidationError('Все товары в заказе должны быть в одной валюте!')


class OrderItemInline(admin.TabularInline):
    """Инлайн для отображения товаров в заказе в админке"""
    model = OrderItem
    extra = 1
    min_num = 1
    formset = OrderItemInlineFormSet
    can_delete = True


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
