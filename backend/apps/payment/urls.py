from django.urls import path
from . import views

urlpatterns = [
    # Shipping Address URLs
    path('shipping-addresses/', views.ShippingAddressListView.as_view(), name='shipping-address-list'),
    path('shipping-addresses/create/', views.ShippingAddressCreateView.as_view(), name='shipping-address-create'),
    path('shipping-addresses/<int:pk>/', views.ShippingAddressDetailView.as_view(), name='shipping-address-detail'),
    path('shipping-addresses/<int:pk>/update/', views.ShippingAddressUpdateView.as_view(), name='shipping-address-update'),
    path('shipping-addresses/<int:pk>/delete/', views.ShippingAddressDeleteView.as_view(), name='shipping-address-delete'),
    path('shipping-addresses/<int:pk>/set-default/', views.ShippingAddressSetDefaultView.as_view(), name='shipping-address-set-default'),

    # Order URLs
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('orders/create/', views.OrderCreateView.as_view(), name='order-create'),
    path('orders/<str:order_number>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/<str:order_number>/cancel/', views.OrderCancelView.as_view(), name='order-cancel'),

    # Coupon URLs
    path('coupons/validate/', views.CouponValidateView.as_view(), name='coupon-validate'),
    path('coupons/', views.CouponListView.as_view(), name='coupon-list'),

    # Payment URLs
    path('payments/<str:order_number>/create/', views.PaymentCreateView.as_view(), name='payment-create'),
    path('payments/<int:pk>/', views.PaymentDetailView.as_view(), name='payment-detail'),

    # Webhook URLs
    path('webhooks/stripe/', views.stripe_webhook, name='stripe-webhook'),

    # Admin URLs
    path('admin/orders/<str:order_number>/status/', views.OrderUpdateStatusView.as_view(), name='order-update-status'),
]
