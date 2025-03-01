from rest_framework import serializers
from .models import Item, Order, OrderItem


class ItemSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Item"""
    display_price = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'price', 'currency', 'display_price']

    def get_display_price(self, obj) -> str:
        """Получение отформатированной цены товара"""
        return obj.get_display_price()


class OrderItemSerializer(serializers.ModelSerializer):
    """Сериализатор для модели OrderItem"""
    item = ItemSerializer(read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(
        queryset=Item.objects.all(),
        source='item',
        write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['item', 'item_id', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Order"""
    items = OrderItemSerializer(source='orderitem_set', many=True)
    total_price = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'created_at', 'items', 'discount', 'tax', 'total_price', 'currency']
        read_only_fields = ['created_at']

    def get_total_price(self, obj) -> int:
        """Получение общей стоимости заказа"""
        return obj.get_total_price()

    def get_currency(self, obj) -> str:
        """Получение валюты заказа или сообщение об ошибке, если товары имеют разные валюты"""
        try:
            return obj.get_currency()
        except ValueError as e:
            return str(e)

    def create(self, validated_data) -> Order:
        """
        Создание объекта Order и связанных OrderItem
        validated_data: Проверенные данные для создания заказа
        """
        items_data = validated_data.pop('orderitem_set')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order

    def validate(self, data) -> dict:
        """
        Проверка, что все товары в заказе имеют одинаковую валюту
        data: Данные для валидации
        """
        items_data = data.get('orderitem_set', [])
        currencies = set(item_data['item'].currency for item_data in items_data)

        if len(currencies) > 1:
            raise serializers.ValidationError("Все товары в заказе должны иметь одинаковую валюту")
        return data
