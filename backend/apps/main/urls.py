from django.urls import path
from . import views

urlpatterns = [
    # Category URLs
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category-create'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('categories/<slug:slug>/update/', views.CategoryUpdateView.as_view(), name='category-update'),
    path('categories/<slug:slug>/delete/', views.CategoryDeleteView.as_view(), name='category-delete'),

    # Brand URLs
    path('brands/', views.BrandListView.as_view(), name='brand-list'),
    path('brands/create/', views.BrandCreateView.as_view(), name='brand-create'),
    path('brands/<slug:slug>/', views.BrandDetailView.as_view(), name='brand-detail'),
    path('brands/<slug:slug>/update/', views.BrandUpdateView.as_view(), name='brand-update'),
    path('brands/<slug:slug>/delete/', views.BrandDeleteView.as_view(), name='brand-delete'),

    # Product URLs
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/create/', views.ProductCreateView.as_view(), name='product-create'),
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('products/<slug:slug>/related/', views.ProductRelatedView.as_view(), name='product-related'),
    path('products/<slug:slug>/update/', views.ProductUpdateView.as_view(), name='product-update'),
    path('products/<slug:slug>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),

    # Product Image URLs
    path('product-images/create/', views.ProductImageCreateView.as_view(), name='product-image-create'),
    path('product-images/<int:pk>/update/', views.ProductImageUpdateView.as_view(), name='product-image-update'),
    path('product-images/<int:pk>/delete/', views.ProductImageDeleteView.as_view(), name='product-image-delete'),

    # Product Variant URLs
    path('product-variants/create/', views.ProductVariantCreateView.as_view(), name='product-variant-create'),
    path('product-variants/<int:pk>/update/', views.ProductVariantUpdateView.as_view(), name='product-variant-update'),
    path('product-variants/<int:pk>/delete/', views.ProductVariantDeleteView.as_view(), name='product-variant-delete'),

    # Review URLs
    path('products/<slug:product_slug>/reviews/', views.ProductReviewListView.as_view(), name='product-reviews'),
    path('products/<slug:product_slug>/reviews/create/', views.ReviewCreateView.as_view(), name='review-create'),
    path('reviews/<int:pk>/update/', views.ReviewUpdateView.as_view(), name='review-update'),
    path('reviews/<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='review-delete'),

    # Wishlist URLs
    path('wishlist/', views.WishlistListView.as_view(), name='wishlist-list'),
    path('wishlist/add/', views.WishlistAddView.as_view(), name='wishlist-add'),
    path('wishlist/remove/<int:product_id>/', views.WishlistRemoveView.as_view(), name='wishlist-remove'),

    # Product Tag URLs
    path('tags/', views.ProductTagListView.as_view(), name='tag-list'),
    path('tags/create/', views.ProductTagCreateView.as_view(), name='tag-create'),
]
