# purchase_orders/urls.py
from django.urls import path
from .views import PurchaseOrderListCreateView, PurchaseOrderRetrieveUpdateDeleteView

urlpatterns = [
    path('api/purchase_orders/', PurchaseOrderListCreateView.as_view(), name='purchase-order-list-create'),
    path('api/purchase_orders/<int:pk>/', PurchaseOrderRetrieveUpdateDeleteView.as_view(), name='purchase-order-retrieve-update-delete'),
]
