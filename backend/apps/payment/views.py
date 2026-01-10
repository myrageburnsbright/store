from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import (
    ShippingAddress, Order, OrderItem, Payment,
    Coupon, OrderStatusHistory
)
from .serializers import (
    ShippingAddressSerializer, OrderSerializer, OrderCreateSerializer,
    CouponSerializer, CouponValidateSerializer, PaymentSerializer
)


# ==================== Shipping Address Views ====================

class ShippingAddressListView(generics.ListAPIView):
    """List user's shipping addresses"""
    serializer_class = ShippingAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ShippingAddress.objects.filter(
            user=self.request.user,
            is_active=True
        )


class ShippingAddressCreateView(generics.CreateAPIView):
    """Create new shipping address"""
    serializer_class = ShippingAddressSerializer
    permission_classes = [permissions.IsAuthenticated]


class ShippingAddressDetailView(generics.RetrieveAPIView):
    """Get shipping address details"""
    serializer_class = ShippingAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)


class ShippingAddressUpdateView(generics.UpdateAPIView):
    """Update shipping address"""
    serializer_class = ShippingAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)


class ShippingAddressDeleteView(generics.DestroyAPIView):
    """Delete (deactivate) shipping address"""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response({
            'message': 'Shipping address removed'
        }, status=status.HTTP_200_OK)


class ShippingAddressSetDefaultView(APIView):
    """Set address as default"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        address = get_object_or_404(
            ShippingAddress,
            pk=pk,
            user=request.user,
            is_active=True
        )

        # Unset other defaults
        ShippingAddress.objects.filter(
            user=request.user
        ).update(is_default=False)

        # Set this as default
        address.is_default = True
        address.save()

        return Response({
            'message': 'Default address updated',
            'address': ShippingAddressSerializer(address).data
        }, status=status.HTTP_200_OK)


# ==================== Order Views ====================

class OrderListView(generics.ListAPIView):
    """List user's orders"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related(
            'items__product',
            'items__variant',
            'shipping_address',
            'status_history'
        ).order_by('-created_at')


class OrderDetailView(generics.RetrieveAPIView):
    """Get order details"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'order_number'

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related(
            'items__product',
            'items__variant',
            'shipping_address',
            'status_history'
        )


class OrderCreateView(generics.CreateAPIView):
    """Create order from cart (checkout)"""
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        return Response({
            'message': 'Order created successfully',
            'order': OrderSerializer(order).data
        }, status=status.HTTP_201_CREATED)


class OrderCancelView(APIView):
    """Cancel order (only if not paid/shipped)"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_number):
        order = get_object_or_404(
            Order,
            order_number=order_number,
            user=request.user
        )

        # Can only cancel if not paid or already cancelled
        if order.status in ['shipped', 'delivered']:
            return Response({
                'error': 'Cannot cancel order that has been shipped or delivered'
            }, status=status.HTTP_400_BAD_REQUEST)

        if order.status == 'cancelled':
            return Response({
                'error': 'Order is already cancelled'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Restore stock
        for item in order.items.all():
            if item.variant:
                item.variant.stock_quantity += item.quantity
                item.variant.save()
            else:
                item.product.stock_quantity += item.quantity
                item.product.save()

            # Update sales count
            item.product.sales_count -= item.quantity
            item.product.save()

        # Update order status
        order.status = 'cancelled'
        order.save()

        # Add to status history
        OrderStatusHistory.objects.create(
            order=order,
            status='cancelled',
            notes='Cancelled by customer',
            changed_by=request.user
        )

        return Response({
            'message': 'Order cancelled successfully',
            'order': OrderSerializer(order).data
        }, status=status.HTTP_200_OK)


# ==================== Coupon Views ====================

class CouponValidateView(APIView):
    """Validate coupon code and calculate discount"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CouponValidateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        coupon = serializer.validated_data['coupon']
        order_amount = serializer.validated_data.get('order_amount', 0)

        discount_amount = 0
        if order_amount:
            discount_amount = coupon.calculate_discount(order_amount)

        return Response({
            'valid': True,
            'coupon': CouponSerializer(coupon).data,
            'discount_amount': discount_amount,
            'message': f'Coupon "{coupon.code}" applied successfully'
        }, status=status.HTTP_200_OK)


class CouponListView(generics.ListAPIView):
    """List active coupons (admin only)"""
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Coupon.objects.filter(is_active=True)


# ==================== Payment Views ====================

class PaymentCreateView(APIView):
    """Process payment for an order"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_number):
        order = get_object_or_404(
            Order,
            order_number=order_number,
            user=request.user
        )

        # Check if already paid
        if order.is_paid:
            return Response({
                'error': 'Order is already paid'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Here you would integrate with payment gateway (Stripe, PayPal, etc.)
        # For now, we'll simulate a successful payment

        # Create payment record
        import uuid
        payment = Payment.objects.create(
            order=order,
            payment_id=f"PAY-{uuid.uuid4().hex[:12].upper()}",
            payment_method=order.payment_method,
            amount=order.total,
            status='completed'
        )

        # Update order
        order.is_paid = True
        order.paid_at = timezone.now()
        order.status = 'paid'
        order.save()

        # Add to status history
        OrderStatusHistory.objects.create(
            order=order,
            status='paid',
            notes='Payment completed',
            changed_by=request.user
        )

        return Response({
            'message': 'Payment processed successfully',
            'payment': PaymentSerializer(payment).data,
            'order': OrderSerializer(order).data
        }, status=status.HTTP_200_OK)


class PaymentDetailView(generics.RetrieveAPIView):
    """Get payment details"""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)


# ==================== Admin Views ====================

class OrderUpdateStatusView(APIView):
    """Update order status (admin only)"""
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number)

        new_status = request.data.get('status')
        notes = request.data.get('notes', '')
        tracking_number = request.data.get('tracking_number', '')

        if not new_status:
            return Response({
                'error': 'Status is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate status
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response({
                'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Update order
        order.status = new_status

        if new_status == 'shipped' and not order.shipped_at:
            order.shipped_at = timezone.now()
            if tracking_number:
                order.tracking_number = tracking_number

        if new_status == 'delivered' and not order.delivered_at:
            order.delivered_at = timezone.now()

        order.save()

        # Add to status history
        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
            notes=notes,
            changed_by=request.user
        )

        return Response({
            'message': f'Order status updated to {new_status}',
            'order': OrderSerializer(order).data
        }, status=status.HTTP_200_OK)
