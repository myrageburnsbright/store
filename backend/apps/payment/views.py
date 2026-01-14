from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.conf import settings
import stripe
import json
from .models import (
    ShippingAddress, Order, OrderItem, Payment,
    Coupon, OrderStatusHistory
)
from .serializers import (
    ShippingAddressSerializer, OrderSerializer, OrderCreateSerializer,
    CouponSerializer, CouponValidateSerializer, PaymentSerializer
)
from .services import StripeService, WebhookService, PaymentService

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
    """List user's orders with optional status filtering"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Order.objects.filter(
            user=self.request.user
        ).prefetch_related(
            'items__product',
            'items__variant',
            'shipping_address',
            'status_history'
        ).order_by('-created_at')

        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset


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
    """Process payment for an order - creates Stripe checkout session"""
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

        # Validate payment method is Stripe
        if order.payment_method != 'stripe':
            return Response({
                'error': 'Only Stripe payments are supported. Please create a new order with Stripe as the payment method.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get success and cancel URLs from request (frontend should provide these)
        frontend_url = request.data.get('frontend_url', settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else 'http://localhost:5173')
        success_url = f"{frontend_url}/checkout/success?order_number={order_number}"
        cancel_url = f"{frontend_url}/checkout/cancel?order_number={order_number}"

        # Validate coupon if provided but DON'T save to order
        # Store coupon code in session metadata for webhook processing
        coupon_code = None
        if request.data.get('coupon_code'):
            try:
                coupon = Coupon.objects.get(code=request.data.get('coupon_code').upper(), is_active=True)
                if coupon.is_valid:
                    coupon_code = coupon.code
            except Coupon.DoesNotExist:
                pass

        # Create Stripe checkout session
        try:
            session = StripeService.create_checkout_session(
                request.user,
                order,
                success_url,
                cancel_url,
                coupon_code=coupon_code
            )

            if not session:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"StripeService.create_checkout_session returned None for order {order_number}")
                return Response({
                    'error': 'Failed to create payment session. Please check Stripe configuration.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            import uuid
            payment = Payment.objects.create(
                order=order,
                payment_id=f"PAY-{uuid.uuid4().hex[:12].upper()}",
                payment_method=order.payment_method,
                amount=order.total,
                currency='USD',
                status='pending',
                stripe_session_id=session['session_id']
            )

            # Return checkout URL for frontend to redirect
            return Response({
                'message': 'Payment session created',
                'checkout_url': session['checkout_url'],
                'session_id': session['session_id'],
                'payment': PaymentSerializer(payment).data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import logging
            import traceback
            logger = logging.getLogger(__name__)
            logger.error(f"Payment processing error for order {order_number}: {str(e)}")
            logger.error(traceback.format_exc())
            return Response({
                'error': f'Payment processing error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


# ==================== Stripe Webhook ====================

@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    # Verify webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    # Process the event through WebhookService
    try:
        WebhookService.process_stripe_webhook(event)
        return JsonResponse({'status': 'success'}, status=200)
    except Exception as e:
        # Log error but return 200 to prevent Stripe from retrying
        print(f"Webhook processing error: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
