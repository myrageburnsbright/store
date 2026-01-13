from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from apps.main.models import Product, ProductVariant


class Cart(models.Model):
    """
    Shopping cart for authenticated users.
    Each user has one cart.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'carts'
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total_items(self):
        """Total number of items in cart"""
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        """Subtotal before any discounts or taxes"""
        return sum(item.original_price * item.quantity for item in self.items.all())

    @property
    def total_discount(self):
        """Total discount amount"""
        return sum(item.discount_amount for item in self.items.all())

    @property
    def total(self):
        """Final total after discounts"""
        return self.subtotal - self.total_discount


class CartItem(models.Model):
    """
    Individual items in a shopping cart.
    Can reference either a base product or a specific variant.
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cart_items',
        help_text="Optional product variant (e.g., size, color)"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cart_items'
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ['cart', 'product', 'variant']
        ordering = ['-created_at']

    def __str__(self):
        if self.variant:
            return f"{self.product.name} - {self.variant.name} (x{self.quantity})"
        return f"{self.product.name} (x{self.quantity})"

    @property
    def unit_price(self):
        """Price per unit (considering variant if exists)"""
        if self.variant:
            return self.variant.final_price
        return self.product.price

    @property
    def original_price(self):
        """Original price per unit before discount"""
        if self.variant:
            base = self.product.base_price + self.variant.price_adjustment
            return base
        return self.product.base_price

    @property
    def total_price(self):
        """Total price for this cart item"""
        return self.unit_price * self.quantity

    @property
    def discount_amount(self):
        """Total discount for this cart item"""
        if self.original_price > self.unit_price:
            return (self.original_price - self.unit_price) * self.quantity
        return 0

    @property
    def is_available(self):
        """Check if item is still available in sufficient quantity"""
        if self.variant:
            return self.variant.is_active and self.variant.stock_quantity >= self.quantity
        return self.product.is_active and self.product.stock_quantity >= self.quantity

    def save(self, *args, **kwargs):
        # Validate stock availability
        if self.variant:
            if self.quantity > self.variant.stock_quantity:
                from django.core.exceptions import ValidationError
                raise ValidationError(f"Only {self.variant.stock_quantity} items available in stock")
        else:
            if self.quantity > self.product.stock_quantity:
                from django.core.exceptions import ValidationError
                raise ValidationError(f"Only {self.product.stock_quantity} items available in stock")

        super().save(*args, **kwargs)
