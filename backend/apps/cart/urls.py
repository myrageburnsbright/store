from django.urls import path
from . import views

urlpatterns = [
    # Cart operations
    path('', views.CartView.as_view(), name='cart-detail'),
    path('add/', views.CartAddItemView.as_view(), name='cart-add-item'),
    path('clear/', views.CartClearView.as_view(), name='cart-clear'),

    # Cart item operations
    path('items/<int:pk>/', views.CartItemDetailView.as_view(), name='cart-item-detail'),
    path('items/<int:item_id>/update/', views.CartUpdateItemView.as_view(), name='cart-update-item'),
    path('items/<int:item_id>/remove/', views.CartRemoveItemView.as_view(), name='cart-remove-item'),
]
