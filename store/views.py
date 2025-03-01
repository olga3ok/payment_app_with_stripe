import stripe
from decouple import config
from django.shortcuts import render
from django.views.generic import DetailView
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Item, Order
from .serializers import ItemSerializer, OrderSerializer


stripe.api_key = config('STRIPLE_API_KEY')


class ItemDetailView(DetailView):
    """Представление для отображения детальной информации о товаре с кнопкой покупки"""
    model = Item
    template_name = 'store/item_detail.html'


class OrderDetailView(DetailView):
    """Представление для отображения детальной информации о товаре с кнопкой покупки"""
    model = Order
    template_name = 'store/order_detail.html'


class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API эндпоинты для работы с товарами
    - GET /api/items/ - список всех товаров
    - GET /api/items/{id}/ - детальная информация о товаре
    - GET /api/items/{id}/buy/ - создание Stripe Checkout Session
    - GET /api/items/{id}/payment_intent/ - создание Stripe Payment Intent
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    @action(detail=True, methods=['get'])
    def buy(self, request, pk=None) -> Response:
        """
        Создание Striple Checkout Session для товара
        :param request: HTTP запрос
        :param pk: ID товара
        :return: JSON с sessionID или сообщением об ошибке
        """
        item = self.get_object()

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': item.currency,
                            'unit_amount_decimal': item.price * 100,
                            'product_data': {
                                'name': item.name,
                                'description': item.description,
                            },
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=request.build_absolute_uri('/success'),
                cancel_url=request.build_absolute_uri(f'/item/{item.id}'),
            )

            return Response({'sessionId': checkout_session.id})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def payment_intent(self, request, pk=None) -> Response:
        """
        Создание Stripe Payment Intent для одного товара
        :param request: HTTP запрос
        :param pk: ID товара
        :return: JSON с clientSecret
        """
        item = self.get_object()

        try:
            intent = stripe.PaymentIntent.create(
                amount=int(item.price) * 100,
                currency=item.currency,
                metadata={
                    'item_id': item.id,
                    'item_name': item.name
                }
            )

            return Response({
                'clientSecret': intent.client_secret
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OrderViewSet(viewsets.ModelViewSet):
    """
    API эндпоинты для работы в заказами:
    - GET /api/orders/ - список всех заказов
    - POST /api/orders/ - создание нового заказа
    - GET /api/orders/{id}/ - детальная информация о заказе
    - PUT/PATCH /api/orders/{id}/ - обновление заказа
    - DELETE /api/orders/{id}/ - удаление заказа
    - GET /api/orders/{id}/buy/ - создание Stripe Checkout Session для заказа
    - GET /api/orders/{id}/payment_intent/ - создание Stripe Payment Intent для заказа
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=True, methods=['get'])
    def buy(self, request, pk=None) -> Response:
        """
        Создание Stripe Checkout Session для заказа
        request: HTTP запрос
        pk: ID заказа
        return: Response: JSON с sessionId или сообщением об ошибке
        """
        order = self.get_object()

        try:
            currency = order.get_currency()

            line_items = []
            for order_item in order.orderitem_set.all():
                line_items.append({
                    'price_data': {
                        'currency': currency,
                        'unit_amount_decimal': order_item.item.price * 100,
                        'product_data': {
                            'name': order_item.item.name,
                            'description': order_item.item.description,
                        },
                    },
                    'quantity': order_item.quantity,
                })

            session_params = {
                'payment_method_types': ['card'],
                'line_items': line_items,
                'mode': 'payment',
                'success_url': request.build_absolute_uri('/success/'),
                'cancel_url': request.build_absolute_uri(f'/order/{order.id}/'),
                'metadata': {
                    'order_id': order.id
                }
            }

            if order.discount:
                # Создаем купон в Stripe
                coupon = stripe.Coupon.create(
                    percent_off=order.discount.percent_off,
                    duration='once',
                    name=order.discount.name
                )
                session_params['discounts'] = [{'coupon': coupon.id}]

            # Добавление налога, если он существует
            if order.tax:
                # Создаем налоговую ставку в Stripe
                tax_rate = stripe.TaxRate.create(
                    display_name=order.tax.name,
                    inclusive=False,
                    percentage=order.tax.percent,
                )

                # Применяем налог ко всем товарам
                for item in session_params['line_items']:
                    item['tax_rates'] = [tax_rate.id]

            checkout_session = stripe.checkout.Session.create(**session_params)

            return Response({'sessionId': checkout_session.id})
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def payment_intent(self, request, pk=None) -> Response:
        """
        Создание Stripe Payment Intent для заказа
        request: HTTP запрос
        pk: ID заказа
        return: Response: JSON с clientSecret или сообщением об ошибке
        """
        order = self.get_object()

        try:
            currency = order.get_currency()

            intent = stripe.PaymentIntent.create(
                amount=int(order.get_total_price()) * 100,
                currency=currency,
                metadata={
                    'order_id': order.id
                }
            )

            return Response({
                'clientSecret': intent.client_secret,
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def api_documentation(request):
    """Представление для отображения документации API"""
    return render(request, 'api_docs/index.html')
