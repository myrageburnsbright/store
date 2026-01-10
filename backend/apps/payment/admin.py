from django.contrib import admin
from .models import (
    ShippingAddress, Order, OrderItem, Payment,
    Coupon, CouponUsage, OrderStatusHistory
)


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'city', 'state', 'country', 'is_default', 'is_active', 'created_at']
    list_filter = ['is_default', 'is_active', 'country', 'state', 'created_at']
    search_fields = ['full_name', 'user__username', 'user__email', 'city', 'phone', 'postal_code']
    list_editable = ['is_default', 'is_active']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'full_name', 'phone')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Settings', {
            'fields': ('is_default', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['product', 'variant', 'product_name', 'quantity', 'unit_price', 'discount_amount', 'total_price']
    readonly_fields = ['product_name', 'total_price']


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    fields = ['status', 'notes', 'changed_by', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'payment_method', 'is_paid',
                    'total', 'created_at']
    list_filter = ['status', 'payment_method', 'is_paid', 'created_at', 'paid_at']
    search_fields = ['order_number', 'user__username', 'user__email', 'tracking_number']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'paid_at',
                       'shipped_at', 'delivered_at']
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status')
        }),
        ('Shipping', {
            'fields': ('shipping_address', 'tracking_number', 'shipped_at', 'delivered_at')
        }),
        ('Payment', {
            'fields': ('payment_method', 'is_paid', 'paid_at')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'discount_amount', 'tax_amount', 'shipping_cost', 'total')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Track status changes"""
        if change and 'status' in form.changed_data:
            OrderStatusHistory.objects.create(
                order=obj,
                status=obj.status,
                notes=f'Status updated by admin',
                changed_by=request.user
            )
        super().save_model(request, obj, form, change)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'variant_name', 'quantity',
                    'unit_price', 'total_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['order__order_number', 'product_name', 'sku']
    readonly_fields = ['created_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'order', 'payment_method', 'amount',
                    'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['payment_id', 'transaction_id', 'order__order_number']
    readonly_fields = ['created_at', 'updated_at', 'raw_response']

    fieldsets = (
        ('Payment Information', {
            'fields': ('order', 'payment_id', 'payment_method', 'amount', 'currency', 'status')
        }),
        ('Transaction Details', {
            'fields': ('transaction_id', 'error_message')
        }),
        ('Raw Response', {
            'fields': ('raw_response',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'used_count',
                    'max_uses', 'is_active', 'valid_from', 'valid_to']
    list_filter = ['discount_type', 'is_active', 'valid_from', 'valid_to']
    search_fields = ['code', 'description']
    list_editable = ['is_active']
    readonly_fields = ['used_count', 'created_at', 'updated_at']

    fieldsets = (
        ('Coupon Information', {
            'fields': ('code', 'description')
        }),
        ('Discount', {
            'fields': ('discount_type', 'discount_value', 'minimum_order_amount')
        }),
        ('Usage Limits', {
            'fields': ('max_uses', 'max_uses_per_user', 'used_count')
        }),
        ('Validity', {
            'fields': ('is_active', 'valid_from', 'valid_to')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ['coupon', 'user', 'order', 'discount_amount', 'used_at']
    list_filter = ['used_at']
    search_fields = ['coupon__code', 'user__username', 'order__order_number']
    readonly_fields = ['used_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'changed_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_number', 'notes']
    readonly_fields = ['created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
