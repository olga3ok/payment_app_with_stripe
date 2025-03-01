from django.db import models
from django.core.validators import MinValueValidator


class Item(models.Model):
    """
    Модель товара с указанием названия, описания, цены и валюты.

    name: Название товара
    description: Описание товара
    price: Цена
    currency: Валюта (USD или EUR)
    """
    CURRENCY_CHOICES = (
        ('usd', 'USD'),
        ('eur', 'EUR'),
    )

    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена", validators=[MinValueValidator(1)])
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='usd', verbose_name="Валюта")

    def __str__(self) -> str:
        return f"{self.name} - {self.get_display_price()} {self.get_currency_display()}"

    def get_display_price(self) -> str:
        """Возвращает отформатированную цену с двумя знаками после запятой"""
        return "{0:.2f}".format(self.price)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


class Order(models.Model):
    """
    Модель заказа, объединяющая несколько товаров с возможностью применения скидки и налога.

    created_at: Дата и время создания заказа
    updated_at: Дата и время последнего обновления заказа
    items: Связь ManyToMany с товарами через модель OrderItem
    discount: Опциональная скидка
    tax: Опциональный налог
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    items = models.ManyToManyField(Item, through='OrderItem', verbose_name="Товары")
    discount = models.ForeignKey(
        'Discount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Скидка"
    )
    tax = models.ForeignKey(
        'Tax',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Налог"
    )

    def __str__(self) -> str:
        return f"Заказ #{self.id} от {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def get_total_price(self) -> int:
        """
        Вычисляет общую стоимость заказа, включая налоги и скидки
        """
        total = float(sum(item.item.price * item.quantity for item in self.orderitem_set.all()))
        # Применение скидки
        if self.discount:
            total -= int(total * (self.discount.percent_off / 100))

        # Применение налога
        if self.tax:
            total += int(total * (self.tax.percent / 100))

        return total

    def get_currency(self) -> str:
        """
        Возвращает валюту заказа. Все товары в заказе должны иметь одинаковую валюту.
        ValueError: Если в заказе есть товары с разными валютами
        """
        currencies = set(item.item.currency for item in self.orderitem_set.all())

        if len(currencies) > 1:
            raise ValueError("Все товары в заказе должны иметь одинаковую валюту")
        return currencies.pop() if currencies else 'usd'

    def get_subtotal(self):
        """
        Вычисляет стоимость товарной позиции (цена товара * количество)
        """
        return float(self.item.price) * self.quantity

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderItem(models.Model):
    """
    Связующая модель между Order и Item с указанием количества
    order: Заказ
    item: Товар
    quantity: Количество товара в заказе
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Заказ")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Количество"
    )

    def __str__(self) -> str:
        return f"{self.quantity} x {self.item.name}"

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"
        unique_together = ('order', 'item')


class Discount(models.Model):
    """
    Модель скидки, которая может быть применена к заказу.
    name: Название скидки
    percent_off: Процент скидки (1-100)
    """
    name = models.CharField(max_length=100, verbose_name="Название")
    percent_off = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Процент скидки (1-100)",
        verbose_name="Процент скидки"
    )

    def __str__(self) -> str:
        return f"{self.name} ({self.percent_off}% off)"

    class Meta:
        verbose_name = "Скидка"
        verbose_name_plural = "Скидки"


class Tax(models.Model):
    """
    Модель налога, который может быть применен к заказу
    name: Название налога
    percent: Процент налога
    """
    name = models.CharField(max_length=100, verbose_name="Название")
    percent = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Процент налога",
        verbose_name="Процент налога"
    )

    def __str__(self) -> str:
        return f"{self.name} ({self.percent}%)"

    class Meta:
        verbose_name = "Налог"
        verbose_name_plural = "Налоги"
