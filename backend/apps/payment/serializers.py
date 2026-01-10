from rest_framework import serializers
from .models import (
    ShippingAddress, Order, OrderItem, Payment,
    Coupon, CouponUsage, OrderStatusHistory
)
from apps.main.models import Product, ProductVariant
from apps.cart.models import Cart
from django.utils import timezone
from django.db import transaction


class ShippingAddressSerializer(serializers.ModelSerializer):
    """Serializer for shipping addresses"""

    class Meta:
        model = ShippingAddress
        fields = [
            'id', 'full_name', 'phone', 'address_line1', 'address_line2',
            'city', 'state', 'postal_code', 'country',
            'is_default', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items"""

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'variant', 'product_name', 'variant_name',
            'sku', 'quantity', 'unit_price', 'discount_amount', 'total_price'
        ]


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for order status history"""
    changed_by_name = serializers.CharField(source='changed_by.username', read_only=True)

    class Meta:
        model = OrderStatusHistory
        fields = ['id', 'status', 'notes', 'changed_by_name', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for viewing orders"""
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = ShippingAddressSerializer(read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'shipping_address', 'status',
            'payment_method', 'is_paid', 'paid_at',
            'subtotal', 'discount_amount', 'tax_amount', 'shipping_cost', 'total',
            'tracking_number', 'shipped_at', 'delivered_at',
            'customer_notes', 'items', 'status_history', 'total_items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'order_number', 'created_at', 'updated_at']


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating orders from cart"""
    shipping_address_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=Order.PAYMENT_METHOD_CHOICES)
    customer_notes = serializers.CharField(required=False, allow_blank=True)
    coupon_code = serializers.CharField(required=False, allow_blank=True)

    def validate_shipping_address_id(self, value):
        """Validate shipping address belongs to user"""
        user = self.context['request'].user
        if not ShippingAddress.objects.filter(id=value, user=user, is_active=True).exists():
            raise serializers.ValidationError("Invalid shipping address")
        return value

    def validate_coupon_code(self, value):
        """Validate coupon code if provided"""
        if not value:
            return value

        try:
            coupon = Coupon.objects.get(code=value)
            if not coupon.is_valid:
                raise serializers.ValidationError("This coupon is not valid")

            # Check user usage limit
            user = self.context['request'].user
            user_usage_count = CouponUsage.objects.filter(
                coupon=coupon,
                user=user
            ).count()

            if user_usage_count >= coupon.max_uses_per_user:
                raise serializers.ValidationError(
                    f"You have already used this coupon {coupon.max_uses_per_user} time(s)"
                )

            return value
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid coupon code")

    @transaction.atomic
    def create(self, validated_data):
        """Create order from user's cart"""
        user = self.context['request'].user

        # Get user's cart
        try:
            cart = Cart.objects.prefetch_related('items__product', 'items__variant').get(user=user)
        except Cart.DoesNotExist:
            raise serializers.ValidationError({"error": "Cart is empty"})

        if not cart.items.exists():
            raise serializers.ValidationError({"error": "Cart is empty"})

        # Calculate totals
        subtotal = cart.subtotal
        discount_from_products = cart.total_discount

        # Apply coupon if provided
        coupon_discount = 0
        coupon = None
        coupon_code = validated_data.get('coupon_code')

        if coupon_code:
            coupon = Coupon.objects.get(code=coupon_code)

            # Check minimum order amount
            if subtotal < coupon.minimum_order_amount:
                raise serializers.ValidationError({
                    "coupon_code": f"Minimum order amount of ${coupon.minimum_order_amount} required"
                })

            coupon_discount = coupon.calculate_discount(subtotal)

        from decimal import Decimal
        # Calculate totals
        total_discount = discount_from_products + coupon_discount
        tax_amount = Decimal(0)  # TODO: Calculate based on shipping address
        shipping_cost = Decimal(10.00)  # TODO: Calculate based on shipping method
        total = subtotal - coupon_discount + tax_amount + shipping_cost

        # Create order
        shipping_address = ShippingAddress.objects.get(id=validated_data['shipping_address_id'])

        order = Order.objects.create(
            user=user,
            shipping_address=shipping_address,
            payment_method=validated_data['payment_method'],
            subtotal=subtotal,
            discount_amount=total_discount,
            tax_amount=tax_amount,
            shipping_cost=shipping_cost,
            total=total,
            customer_notes=validated_data.get('customer_notes', '')
        )

        # Create order items from cart
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                variant=cart_item.variant,
                product_name=cart_item.product.name,
                variant_name=cart_item.variant.name if cart_item.variant else '',
                sku=cart_item.variant.sku if cart_item.variant else cart_item.product.sku,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                discount_amount=cart_item.discount_amount,
                total_price=cart_item.total_price
            )

            # Update product stock
            if cart_item.variant:
                cart_item.variant.stock_quantity -= cart_item.quantity
                cart_item.variant.save()
            else:
                cart_item.product.stock_quantity -= cart_item.quantity
                cart_item.product.save()

            # Update product sales count
            cart_item.product.sales_count += cart_item.quantity
            cart_item.product.save()

        # Create coupon usage record if applicable
        if coupon:
            CouponUsage.objects.create(
                coupon=coupon,
                user=user,
                order=order,
                discount_amount=coupon_discount
            )
            coupon.used_count += 1
            coupon.save()

        # Create initial status history
        OrderStatusHistory.objects.create(
            order=order,
            status='pending',
            notes='Order created',
            changed_by=user
        )

        # Clear cart
        cart.items.all().delete()

        return order


class CouponSerializer(serializers.ModelSerializer):
    """Serializer for coupons"""
    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'description', 'discount_type', 'discount_value',
            'minimum_order_amount', 'max_uses', 'max_uses_per_user',
            'used_count', 'is_active', 'is_valid',
            'valid_from', 'valid_to', 'created_at'
        ]


class CouponValidateSerializer(serializers.Serializer):
    """Serializer for validating coupon codes"""
    code = serializers.CharField()
    order_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    def validate(self, attrs):
        code = attrs['code']
        user = self.context['request'].user

        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            raise serializers.ValidationError({"code": "Invalid coupon code"})

        # Check if coupon is valid
        if not coupon.is_valid:
            raise serializers.ValidationError({"code": "This coupon is not valid or has expired"})

        # Check user usage limit
        user_usage_count = CouponUsage.objects.filter(coupon=coupon, user=user).count()
        if user_usage_count >= coupon.max_uses_per_user:
            raise serializers.ValidationError({
                "code": f"You have already used this coupon {coupon.max_uses_per_user} time(s)"
            })

        # Check minimum order amount if provided
        order_amount = attrs.get('order_amount')
        if order_amount and order_amount < coupon.minimum_order_amount:
            raise serializers.ValidationError({
                "code": f"Minimum order amount of ${coupon.minimum_order_amount} required"
            })

        attrs['coupon'] = coupon
        return attrs


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments"""

    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'payment_id', 'payment_method',
            'amount', 'currency', 'status', 'transaction_id',
            'error_message', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
