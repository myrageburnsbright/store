from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import (
    CartSerializer, CartItemSerializer, CartItemCreateSerializer,
    CartItemUpdateSerializer
)


class CartView(APIView):
    """
    Get user's cart with all items.
    Creates cart automatically if it doesn't exist.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart = Cart.objects.prefetch_related(
            'items__product__images',
            'items__product__category',
            'items__product__brand',
            'items__variant'
        ).get(id=cart.id)

        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartAddItemView(APIView):
    """
    Add item to cart or update quantity if item already exists.
    Returns the full cart object with all items.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Get or create cart for user
        cart, created = Cart.objects.get_or_create(user=request.user)

        serializer = CartItemCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data['product']
        variant = serializer.validated_data.get('variant')
        quantity = serializer.validated_data['quantity']

        # Check if item already exists in cart
        existing_item = CartItem.objects.filter(
            cart=cart,
            product=product,
            variant=variant
        ).first()

        if existing_item:
            # Update quantity of existing item
            new_quantity = existing_item.quantity + quantity

            # Validate new quantity against stock
            if variant:
                if new_quantity > variant.stock_quantity:
                    return Response({
                        'error': f'Cannot add {quantity} more. Only {variant.stock_quantity} items available in stock'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                if new_quantity > product.stock_quantity:
                    return Response({
                        'error': f'Cannot add {quantity} more. Only {product.stock_quantity} items available in stock'
                    }, status=status.HTTP_400_BAD_REQUEST)

            existing_item.quantity = new_quantity
            existing_item.save()
        else:
            # Create new cart item
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                variant=variant,
                quantity=quantity
            )

        # Refresh cart with all related data and return full cart
        cart = Cart.objects.prefetch_related(
            'items__product__images',
            'items__product__category',
            'items__product__brand',
            'items__variant'
        ).get(id=cart.id)

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartUpdateItemView(APIView):
    """
    Update quantity of a specific cart item.
    Returns the full cart object with all items.
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, item_id):
        # Get cart item and verify ownership
        cart_item = get_object_or_404(
            CartItem,
            id=item_id,
            cart__user=request.user
        )

        serializer = CartItemUpdateSerializer(
            data=request.data,
            context={'cart_item': cart_item}
        )
        serializer.is_valid(raise_exception=True)

        cart_item.quantity = serializer.validated_data['quantity']
        cart_item.save()

        # Return full cart object
        cart = Cart.objects.prefetch_related(
            'items__product__images',
            'items__product__category',
            'items__product__brand',
            'items__variant'
        ).get(id=cart_item.cart.id)

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartRemoveItemView(APIView):
    """
    Remove specific item from cart.
    Returns the full cart object with remaining items.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, item_id):
        # Get cart item and verify ownership
        cart_item = get_object_or_404(
            CartItem,
            id=item_id,
            cart__user=request.user
        )

        cart_id = cart_item.cart.id
        cart_item.delete()

        # Return full cart object
        cart = Cart.objects.prefetch_related(
            'items__product__images',
            'items__product__category',
            'items__product__brand',
            'items__variant'
        ).get(id=cart_id)

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartClearView(APIView):
    """
    Clear all items from cart.
    Returns the empty cart object.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()

        # Return empty cart object
        cart = Cart.objects.prefetch_related(
            'items__product__images',
            'items__product__category',
            'items__product__brand',
            'items__variant'
        ).get(id=cart.id)

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartItemDetailView(generics.RetrieveAPIView):
    """
    Get details of a specific cart item.
    """
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(
            cart__user=self.request.user
        ).select_related('product', 'variant', 'cart')
