from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.urls import reverse


class Category(models.Model):
    """
    Product categories with hierarchical structure (parent-child relationships).
    Examples: Electronics > Smartphones > Android Phones
    """
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('category-detail', kwargs={'slug': self.slug})

    @property
    def products_count(self):
        """Get total products in this category and subcategories"""
        count = self.products.filter(is_active=True).count()
        print(count)
        for child in self.children.all():
            count += child.products_count
        return count


class Brand(models.Model):
    """
    Product brands/manufacturers.
    Examples: Apple, Samsung, Nike, Adidas
    """
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brands/', null=True, blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'brands'
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """
    Main product model.
    Each product can have multiple variants (sizes, colors, etc.)
    """
    name = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    description = models.TextField()
    short_description = models.TextField(max_length=500, blank=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products'
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )

    # Pricing
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )

    # Stock tracking (for simple products without variants)
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=10)

    # Product attributes
    sku = models.CharField(max_length=100, unique=True, blank=True)
    weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight in kg"
    )

    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)

    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=300, blank=True)
    meta_keywords = models.CharField(max_length=300, blank=True)

    # Statistics
    views_count = models.PositiveIntegerField(default=0)
    sales_count = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['is_active', '-created_at']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['category', 'is_active']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        # Generate SKU after first save to ensure we have an ID
        generate_sku = not self.sku
        if generate_sku and not self.pk:
            # First save without SKU to get ID
            super().save(*args, **kwargs)
            self.sku = f"PRD-{self.id}"
            kwargs['force_insert'] = False

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product-detail', kwargs={'slug': self.slug})

    @property
    def price(self):
        """Returns discount price if available, otherwise base price"""
        return self.discount_price if self.discount_price else self.base_price

    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.discount_price and self.discount_price < self.base_price:
            return int(((self.base_price - self.discount_price) / self.base_price) * 100)
        return 0

    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        return self.stock_quantity > 0

    @property
    def is_low_stock(self):
        """Check if stock is low"""
        return 0 < self.stock_quantity <= self.low_stock_threshold

    @property
    def average_rating(self):
        """Calculate average rating from reviews"""
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return 0

    @property
    def reviews_count(self):
        """Count approved reviews"""
        return self.reviews.filter(is_approved=True).count()


class ProductImage(models.Model):
    """
    Product images - multiple images per product.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_images'
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.product.name} - Image {self.id}"

    def save(self, *args, **kwargs):
        # If this is set as primary, unset other primary images for this product
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductVariant(models.Model):
    """
    Product variants (e.g., different sizes, colors).
    Example: iPhone 15 Pro - 256GB Black
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants'
    )
    name = models.CharField(max_length=200)  # e.g., "256GB Black"
    sku = models.CharField(max_length=100, unique=True, blank=True)

    # Price adjustment (added to base product price)
    # Example: +200 for larger storage, -50 for sale variant
    price_adjustment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Amount to add/subtract from base product price"
    )

    # Stock
    stock_quantity = models.PositiveIntegerField(default=0)

    # Variant attributes (stored as JSON for flexibility)
    # Example: {"color": "Black", "size": "256GB", "material": "Titanium"}
    attributes = models.JSONField(default=dict, blank=True)

    image = models.ImageField(upload_to='variants/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product_variants'
        verbose_name = 'Product Variant'
        verbose_name_plural = 'Product Variants'
        ordering = ['product', 'name']

    def __str__(self):
        return f"{self.product.name} - {self.name}"

    def save(self, *args, **kwargs):
        # Generate SKU after first save to ensure we have an ID
        generate_sku = not self.sku
        if generate_sku and not self.pk:
            # First save without SKU to get ID
            super().save(*args, **kwargs)
            self.sku = f"VAR-{self.product.id}-{self.id}"
            kwargs['force_insert'] = False

        super().save(*args, **kwargs)

    @property
    def final_price(self):
        """Returns product price + variant adjustment"""
        base = self.product.discount_price if self.product.discount_price else self.product.base_price
        return base + self.price_adjustment

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0


class Review(models.Model):
    """
    Product reviews and ratings.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='product_reviews'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200)
    comment = models.TextField()

    # Review status
    is_approved = models.BooleanField(default=False)
    is_verified_purchase = models.BooleanField(default=False)

    # Helpfulness tracking
    helpful_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product_reviews'
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        unique_together = ['product', 'user']  # One review per user per product
        indexes = [
            models.Index(fields=['product', 'is_approved']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating}⭐"


class Wishlist(models.Model):
    """
    User wishlist/favorites.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishlist_items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='wishlisted_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wishlists'
        verbose_name = 'Wishlist Item'
        verbose_name_plural = 'Wishlist Items'
        unique_together = ['user', 'product']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class ProductTag(models.Model):
    """
    Tags for products (e.g., "summer sale", "trending", "bestseller").
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_tags'
        verbose_name = 'Product Tag'
        verbose_name_plural = 'Product Tags'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# Many-to-many relationship between Product and Tag
class ProductTagAssociation(models.Model):
    """
    Association between products and tags.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_tags'
    )
    tag = models.ForeignKey(
        ProductTag,
        on_delete=models.CASCADE,
        related_name='tagged_products'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_tag_associations'
        unique_together = ['product', 'tag']
        ordering = ['product']

    def __str__(self):
        return f"{self.product.name} - {self.tag.name}"
