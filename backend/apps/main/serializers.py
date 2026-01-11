from rest_framework import serializers
from .models import (
    Category, Brand, Product, ProductImage, ProductVariant,
    Review, Wishlist, ProductTag
)
from django.contrib.auth import get_user_model

User = get_user_model()


class CategoryListSerializer(serializers.ModelSerializer):
    """For displaying categories in lists"""
    products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'is_active', 'products_count']
        read_only_fields = ['slug']


class CategoryDetailSerializer(serializers.ModelSerializer):
    """For detailed category view with parent/children info"""
    products_count = serializers.IntegerField(read_only=True)
    parent = CategoryListSerializer(read_only=True)
    children = CategoryListSerializer(many=True, read_only=True)
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='parent',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 'parent_id',
                  'children', 'image', 'is_active', 'order', 'products_count',
                  'created_at', 'updated_at']
        read_only_fields = ['slug', 'created_at', 'updated_at']


class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    """For creating/updating categories"""

    class Meta:
        model = Category
        fields = ['name', 'description', 'parent', 'is_active', 'order']
        read_only_fields = []


class BrandSerializer(serializers.ModelSerializer):
    """For brand CRUD operations"""
    products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'description', 'logo', 'website',
                  'is_active', 'products_count', 'created_at']
        read_only_fields = ['slug', 'created_at']


class ProductImageSerializer(serializers.ModelSerializer):
    """For product images"""
    class Meta:
        model = ProductImage
        fields = ['product', 'id', 'image', 'alt_text', 'is_primary', 'order']


class ProductVariantSerializer(serializers.ModelSerializer):
    """For product variants (sizes, colors, etc.)"""
    is_in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'sku', 'price', 'attributes', 'stock_quantity',
                  'is_in_stock', 'is_active', 'image']


class ProductTagSerializer(serializers.ModelSerializer):
    """For product tags"""

    class Meta:
        model = ProductTag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']


class ReviewSerializer(serializers.ModelSerializer):
    """For product reviews"""
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'user_name', 'rating', 'title', 'comment',
                  'is_approved', 'created_at', 'updated_at']
        read_only_fields = ['user', 'is_approved', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Automatically set the user from request context
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ProductListSerializer(serializers.ModelSerializer):
    """For product listing pages - minimal data for performance"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'short_description', 'category_name',
                  'brand_name', 'base_price', 'discount_price', 'price',
                  'discount_percentage', 'average_rating', 'reviews_count',
                  'is_in_stock', 'is_featured', 'is_new', 'primary_image']

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ProductImageSerializer(primary_image).data
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """For detailed product view - all data including images, variants, reviews"""
    category = CategoryListSerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    tags = ProductTagSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'short_description',
                  'category', 'brand', 'base_price', 'discount_price', 'price',
                  'discount_percentage', 'stock_quantity', 'low_stock_threshold',
                  'is_in_stock', 'sku', 'weight', 'is_active', 'is_featured',
                  'is_new', 'average_rating', 'reviews_count', 'views_count',
                  'sales_count', 'meta_title', 'meta_description', 'meta_keywords',
                  'published_at', 'created_at', 'updated_at', 'images', 'variants',
                  'reviews', 'tags']


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """For creating and updating products"""
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=ProductTag.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='tags'
    )

    class Meta:
        model = Product
        fields = ['name', 'slug', 'description', 'short_description', 'category',
                  'brand', 'base_price', 'discount_price', 'stock_quantity',
                  'low_stock_threshold', 'sku', 'weight', 'is_active', 'is_featured',
                  'is_new', 'meta_title', 'meta_description', 'meta_keywords',
                  'published_at', 'images', 'variants', 'tag_ids']
        read_only_fields = ['slug']

    def validate(self, attrs):
        # Ensure discount_price is less than base_price if provided
        discount_price = attrs.get('discount_price')
        base_price = attrs.get('base_price')

        if discount_price and base_price and discount_price >= base_price:
            raise serializers.ValidationError({
                'discount_price': 'Discount price must be less than base price'
            })

        return attrs


class WishlistSerializer(serializers.ModelSerializer):
    """For user wishlist"""
    product = ProductListSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
        source='product',
        write_only=True
    )

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'product', 'product_id', 'created_at']
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        # Automatically set the user from request context
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
