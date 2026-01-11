from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, Avg
from .models import (
    Category, Brand, Product, ProductImage, ProductVariant,
    Review, Wishlist, ProductTag
)
from .serializers import (
    CategoryListSerializer, CategoryDetailSerializer, CategoryCreateUpdateSerializer,
    BrandSerializer, ProductListSerializer, ProductDetailSerializer,
    ProductCreateUpdateSerializer, ProductImageSerializer, ProductVariantSerializer,
    ReviewSerializer, WishlistSerializer, ProductTagSerializer
)


# ==================== Category Views ====================

class CategoryListView(generics.ListAPIView):
    """List all active categories with products count"""
    serializer_class = CategoryListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'order', 'created_at']
    ordering = ['order', 'name']

    def get_queryset(self):
        queryset = Category.objects.filter(is_active=True)

        # Filter by parent category if specified
        parent_id = self.request.query_params.get('parent', None)
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        elif parent_id is None and self.request.query_params.get('root', None) == 'true':
            # Get only root categories (no parent)
            queryset = queryset.filter(parent__isnull=True)

        return queryset


class CategoryDetailView(generics.RetrieveAPIView):
    """Get category details with parent and children"""
    serializer_class = CategoryDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return Category.objects.filter(is_active=True).prefetch_related('children', 'parent')


class CategoryCreateView(generics.CreateAPIView):
    """Create new category (admin only)"""
    serializer_class = CategoryCreateUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Category.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()

        return Response({
            'message': 'Category created successfully',
            'category': CategoryDetailSerializer(category).data
        }, status=status.HTTP_201_CREATED)


class CategoryUpdateView(generics.UpdateAPIView):
    """Update category (admin only)"""
    serializer_class = CategoryCreateUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Category.objects.all()
    lookup_field = 'slug'

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({
            'message': 'Category updated successfully'
        }, status=status.HTTP_200_OK)


class CategoryDeleteView(generics.DestroyAPIView):
    """Delete category (admin only)"""
    permission_classes = [permissions.IsAdminUser]
    queryset = Category.objects.all()
    lookup_field = 'slug'

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({
            'message': 'Category deleted successfully'
        }, status=status.HTTP_200_OK)


# ==================== Brand Views ====================

class BrandListView(generics.ListAPIView):
    """List all active brands"""
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        return Brand.objects.filter(is_active=True).annotate(
            products_count=Count('products', filter=Q(products__is_active=True))
        )


class BrandDetailView(generics.RetrieveAPIView):
    """Get brand details"""
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return Brand.objects.filter(is_active=True).annotate(
            products_count=Count('products', filter=Q(products__is_active=True))
        )


class BrandCreateView(generics.CreateAPIView):
    """Create new brand (admin only)"""
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Brand.objects.all()




class BrandUpdateView(generics.UpdateAPIView):
    """Update brand (admin only)"""
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Brand.objects.all()
    lookup_field = 'slug'


class BrandDeleteView(generics.DestroyAPIView):
    """Delete brand (admin only)"""
    permission_classes = [permissions.IsAdminUser]
    queryset = Brand.objects.all()
    lookup_field = 'slug'

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)
        return Response({
            'message': "Deletet successfully",
        }, status=status.HTTP_200_OK)

# ==================== Product Views ====================

class ProductListView(generics.ListAPIView):
    """List products with filtering, search, and ordering"""
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'brand__slug', 'is_featured', 'is_new']
    search_fields = ['name', 'description', 'short_description', 'sku']
    ordering_fields = ['created_at', 'base_price', 'sales_count', 'views_count']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related(
            'category', 'brand'
        ).prefetch_related('images')

        # Filter by price range
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(base_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(base_price__lte=max_price)

        # Filter by rating
        min_rating = self.request.query_params.get('min_rating', None)
        if min_rating:
            queryset = queryset.annotate(
                avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))
            ).filter(avg_rating__gte=min_rating)

        # Filter by stock availability
        in_stock = self.request.query_params.get('in_stock', None)
        if in_stock == 'true':
            queryset = queryset.filter(stock_quantity__gt=0)

        return queryset


class ProductDetailView(generics.RetrieveAPIView):
    """Get product details and increment views count"""
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related(
            'category', 'brand'
        ).prefetch_related(
            'images', 'variants', 'reviews__user', 'product_tags'
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment views count
        instance.views_count += 1
        instance.save(update_fields=['views_count'])

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ProductCreateView(generics.CreateAPIView):
    """Create new product (admin only)"""
    serializer_class = ProductCreateUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Product.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        return Response({
            'message': 'Product created successfully',
            'product': ProductDetailSerializer(product).data
        }, status=status.HTTP_201_CREATED)


class ProductUpdateView(generics.UpdateAPIView):
    """Update product (admin only)"""
    serializer_class = ProductCreateUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Product.objects.all()
    lookup_field = 'slug'

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({
            'message': 'Product updated successfully'
        }, status=status.HTTP_200_OK)


class ProductDeleteView(generics.DestroyAPIView):
    """Delete product (admin only)"""
    permission_classes = [permissions.IsAdminUser]
    queryset = Product.objects.all()
    lookup_field = 'slug'

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({
            'message': 'Product deleted successfully'
        }, status=status.HTTP_200_OK)


# ==================== Product Image Views ====================

class ProductImageCreateView(generics.CreateAPIView):
    """Add image to product (admin only)"""
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ProductImage.objects.all()


class ProductImageUpdateView(generics.UpdateAPIView):
    """Update product image (admin only)"""
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ProductImage.objects.all()


class ProductImageDeleteView(generics.DestroyAPIView):
    """Delete product image (admin only)"""
    permission_classes = [permissions.IsAdminUser]
    queryset = ProductImage.objects.all()


# ==================== Product Variant Views ====================

class ProductVariantCreateView(generics.CreateAPIView):
    """Add variant to product (admin only)"""
    serializer_class = ProductVariantSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ProductVariant.objects.all()


class ProductVariantUpdateView(generics.UpdateAPIView):
    """Update product variant (admin only)"""
    serializer_class = ProductVariantSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ProductVariant.objects.all()


class ProductVariantDeleteView(generics.DestroyAPIView):
    """Delete product variant (admin only)"""
    permission_classes = [permissions.IsAdminUser]
    queryset = ProductVariant.objects.all()


# ==================== Review Views ====================

class ProductReviewListView(generics.ListAPIView):
    """List approved reviews for a product"""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        product_slug = self.kwargs.get('product_slug')
        return Review.objects.filter(
            product__slug=product_slug,
            is_approved=True
        ).select_related('user').order_by('-created_at')


class ReviewCreateView(generics.CreateAPIView):
    """Create review for a product (authenticated users only)"""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        product_slug = self.kwargs.get('product_slug')

        # Check if product exists
        try:
            product = Product.objects.get(slug=product_slug)
        except Product.DoesNotExist:
            return Response({
                'error': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if user already reviewed this product
        if Review.objects.filter(product=product, user=request.user).exists():
            return Response({
                'error': 'You have already reviewed this product'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)

        return Response({
            'message': 'Review submitted successfully and is pending approval',
            'review': serializer.data
        }, status=status.HTTP_201_CREATED)


class ReviewUpdateView(generics.UpdateAPIView):
    """Update own review"""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)


class ReviewDeleteView(generics.DestroyAPIView):
    """Delete own review"""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)


# ==================== Wishlist Views ====================

class WishlistListView(generics.ListAPIView):
    """List user's wishlist"""
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related(
            'product__category', 'product__brand'
        ).prefetch_related('product__images').order_by('-created_at')


class WishlistAddView(generics.CreateAPIView):
    """Add product to wishlist"""
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Check if product already in wishlist
        product_id = request.data.get('product_id')
        if Wishlist.objects.filter(user=request.user, product_id=product_id).exists():
            return Response({
                'error': 'Product already in wishlist'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'message': 'Product added to wishlist',
            'wishlist_item': serializer.data
        }, status=status.HTTP_201_CREATED)


class WishlistRemoveView(APIView):
    """Remove product from wishlist"""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, product_id):
        try:
            wishlist_item = Wishlist.objects.get(user=request.user, product_id=product_id)
            wishlist_item.delete()
            return Response({
                'message': 'Product removed from wishlist'
            }, status=status.HTTP_200_OK)
        except Wishlist.DoesNotExist:
            return Response({
                'error': 'Product not in wishlist'
            }, status=status.HTTP_404_NOT_FOUND)


# ==================== Product Tag Views ====================

class ProductTagListView(generics.ListAPIView):
    """List all product tags"""
    serializer_class = ProductTagSerializer
    permission_classes = [permissions.AllowAny]
    queryset = ProductTag.objects.all().order_by('name')


class ProductTagCreateView(generics.CreateAPIView):
    """Create new tag (admin only)"""
    serializer_class = ProductTagSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ProductTag.objects.all()
