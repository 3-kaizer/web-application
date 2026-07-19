from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Customer


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'product_count')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'subtotal')
    fields = ('product', 'quantity', 'price', 'subtotal')
    
    def subtotal(self, obj):
        if obj.price is None or obj.quantity is None:
            return '—'
        return obj.subtotal
    subtotal.short_description = 'Subtotal'


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'image_thumbnail', 'name', 'category', 'price', 'stock', 'stock_status',
        'is_available', 'availability_badge', 'rating', 'created_at',
    )
    list_filter = ('category', 'is_available', 'created_at')
    search_fields = ('name', 'description', 'category__name')
    list_editable = ('price', 'stock', 'is_available')
    list_select_related = ('category',)
    date_hierarchy = 'created_at'
    readonly_fields = ('slug', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description', 'specifications')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock', 'is_available')
        }),
        ('Rating', {
            'fields': ('rating', 'review_count'),
            'classes': ('collapse',)
        }),
        ('Media', {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Image')
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img class="audiolux-thumbnail" src="{}" alt="{}">',
                obj.image.url,
                obj.name,
            )
        return format_html('<span class="audiolux-thumbnail-placeholder">No image</span>')

    @admin.display(description='Stock', ordering='stock')
    def stock_status(self, obj):
        if obj.stock == 0:
            label, css_class = 'Out of stock', 'is-out'
        elif obj.stock <= 5:
            label, css_class = 'Low stock', 'is-low'
        else:
            label, css_class = 'In stock', 'is-in'
        return format_html('<span class="audiolux-badge {}">{}</span>', css_class, label)

    @admin.display(description='Availability', ordering='is_available')
    def availability_badge(self, obj):
        label = 'Available' if obj.is_available else 'Hidden'
        css_class = 'is-available' if obj.is_available else 'is-hidden'
        return format_html('<span class="audiolux-badge {}">{}</span>', css_class, label)


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'customer_name', 'email', 'total_amount', 'payment_method',
        'payment_status_badge', 'created_at',
    )
    list_filter = ('payment_status', 'payment_method', 'country', 'created_at')
    search_fields = ('id', 'email', 'first_name', 'last_name', 'user__username')
    list_select_related = ('user',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]
    fieldsets = (
        ('Customer Information', {
            'fields': ('user', 'session_id', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('address', 'city', 'postal_code', 'country')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_status', 'transaction_id', 'total_amount')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Customer', ordering='last_name')
    def customer_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'

    @admin.display(description='Payment status', ordering='payment_status')
    def payment_status_badge(self, obj):
        status_classes = {
            'completed': 'is-complete',
            'pending': 'is-pending',
            'failed': 'is-failed',
        }
        return format_html(
            '<span class="audiolux-badge {}">{}</span>',
            status_classes.get(obj.payment_status, 'is-pending'),
            obj.get_payment_status_display(),
        )


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'subtotal')
    list_filter = ('order__payment_status',)
    search_fields = ('product__name', 'order__id', 'order__email')


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'phone', 'city', 'country', 'date_registered')
    search_fields = ('user__username', 'email', 'phone', 'city')
    list_filter = ('country', 'date_registered')
    list_select_related = ('user',)
    date_hierarchy = 'date_registered'
    readonly_fields = ('date_registered',)


class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_id', 'total_items', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'session_id')
    readonly_fields = ('created_at', 'updated_at')


class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'subtotal', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('product__name', 'cart__user__username')