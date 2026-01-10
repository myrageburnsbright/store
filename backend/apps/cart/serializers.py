from rest_framework import serializers
from .models import Cart, CartItem
from apps.main.serializers import ProductListSerializer, ProductVariantSerializer
from apps.main.models import Product, ProductVariant


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items with product details"""
    product = ProductListSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    original_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'variant', 'quantity',
            'unit_price', 'original_price', 'total_price',
            'discount_amount', 'is_available', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CartItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating cart items"""
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
        source='product',
        write_only=True
    )
    variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.filter(is_active=True),
        source='variant',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = CartItem
        fields = ['product_id', 'variant_id', 'quantity']

    def validate_quantity(self, value):
        """Validate quantity is positive"""
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value

    def validate(self, attrs):
        """Validate stock availability"""
        product = attrs.get('product')
        variant = attrs.get('variant')
        quantity = attrs.get('quantity', 1)

        # Check if variant belongs to product
        if variant and variant.product != product:
            raise serializers.ValidationError({
                'variant_id': 'This variant does not belong to the selected product'
            })

        # Check stock availability
        if variant:
            if quantity > variant.stock_quantity:
                raise serializers.ValidationError({
                    'quantity': f'Only {variant.stock_quantity} items available in stock'
                })
        else:
            if quantity > product.stock_quantity:
                raise serializers.ValidationError({
                    'quantity': f'Only {product.stock_quantity} items available in stock'
                })

        return attrs


class CartSerializer(serializers.ModelSerializer):
    """Serializer for user's cart with all items"""
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_discount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'items', 'total_items',
            'subtotal', 'total_discount', 'total',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']


class CartItemUpdateSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity"""
    quantity = serializers.IntegerField(min_value=1)

    def validate_quantity(self, value):
        """Validate quantity against stock"""
        cart_item = self.context.get('cart_item')
        if cart_item:
            if cart_item.variant:
                if value > cart_item.variant.stock_quantity:
                    raise serializers.ValidationError(
                        f'Only {cart_item.variant.stock_quantity} items available in stock'
                    )
            else:
                if value > cart_item.product.stock_quantity:
                    raise serializers.ValidationError(
                        f'Only {cart_item.product.stock_quantity} items available in stock'
                    )
        return value
