from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ['product', 'variant', 'quantity', 'created_at']
    readonly_fields = ['created_at']
    raw_id_fields = ['product', 'variant']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_items', 'subtotal', 'total', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'total_items', 'subtotal', 'total_discount', 'total']
    inlines = [CartItemInline]

    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Cart Summary', {
            'fields': ('total_items', 'subtotal', 'total_discount', 'total')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def total_items(self, obj):
        return obj.total_items
    total_items.short_description = 'Total Items'

    def subtotal(self, obj):
        return f"${obj.subtotal:.2f}"
    subtotal.short_description = 'Subtotal'

    def total(self, obj):
        return f"${obj.total:.2f}"
    total.short_description = 'Total'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'variant', 'quantity', 'unit_price', 'total_price', 'is_available', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['cart__user__username', 'product__name', 'variant__name']
    readonly_fields = ['created_at', 'updated_at', 'unit_price', 'original_price', 'total_price', 'discount_amount', 'is_available']
    raw_id_fields = ['cart', 'product', 'variant']

    fieldsets = (
        ('Cart Item Information', {
            'fields': ('cart', 'product', 'variant', 'quantity')
        }),
        ('Pricing', {
            'fields': ('unit_price', 'original_price', 'total_price', 'discount_amount')
        }),
        ('Availability', {
            'fields': ('is_available',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def unit_price(self, obj):
        return f"${obj.unit_price:.2f}"
    unit_price.short_description = 'Unit Price'

    def total_price(self, obj):
        return f"${obj.total_price:.2f}"
    total_price.short_description = 'Total Price'
