from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Customer
from .admin_site import AudioLuxAdminSite

# Define ModelAdmin classes first
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
        return obj.subtotal
    subtotal.short_description = 'Subtotal'


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_available', 'rating', 'created_at')
    list_filter = ('category', 'is_available', 'created_at')
    search_fields = ('name', 'description', 'category__name')
    list_editable = ('price', 'stock', 'is_available')
    readonly_fields = ('slug', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('name',)}
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


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'email', 'total_amount', 'payment_method', 'payment_status', 'created_at')
    list_filter = ('payment_status', 'payment_method', 'created_at')
    search_fields = ('id', 'email', 'first_name', 'last_name', 'user__username')
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


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'subtotal')
    list_filter = ('order__payment_status',)
    search_fields = ('product__name', 'order__id', 'order__email')


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'phone', 'city', 'country', 'date_registered')
    search_fields = ('user__username', 'email', 'phone', 'city')
    list_filter = ('country', 'date_registered')
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


# Create custom admin site instance and register models after classes are defined
audio_lux_admin = AudioLuxAdminSite(name='audio_lux_admin')

audio_lux_admin.register(Category, CategoryAdmin)
audio_lux_admin.register(Product, ProductAdmin)
audio_lux_admin.register(Customer, CustomerAdmin)
audio_lux_admin.register(Order, OrderAdmin)
audio_lux_admin.register(OrderItem, OrderItemAdmin)
audio_lux_admin.register(Cart, CartAdmin)
audio_lux_admin.register(CartItem, CartItemAdmin)