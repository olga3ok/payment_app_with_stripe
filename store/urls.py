from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView
from .views import ItemDetailView, ItemViewSet, OrderViewSet, OrderDetailView, api_documentation


router = DefaultRouter()
router.register(r'items', ItemViewSet)
router.register(r'orders', OrderViewSet)


urlpatterns = [
    path('api/', include(router.urls)),
    path('api/docs/', api_documentation, name='api_documentation'),

    path('item/<int:pk>/', ItemDetailView.as_view(), name='item-detail'),
    path('order/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('success/', TemplateView.as_view(template_name='store/success.html'), name='success'),
    path('main/', TemplateView.as_view(template_name='store/main.html'), name='main'),
]
