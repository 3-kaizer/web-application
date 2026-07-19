from django.contrib import admin
from .models import Order, Product, Customer, Category, Cart, CartItem, OrderItem
from .admin_admins import (
    CategoryAdmin, ProductAdmin, OrderAdmin, OrderItemAdmin,
    CustomerAdmin, CartAdmin, CartItemAdmin, OrderItemInline
)


class AudioLuxAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        """
        Custom admin index with dashboard stats.
        """
        # Get counts
        orders_count = Order.objects.count()
        products_count = Product.objects.count()
        customers_count = Customer.objects.count()
        categories_count = Category.objects.count()

        # Get recent orders (last 5)
        recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]

        # Get low stock products (stock < 5)
        low_stock_products = Product.objects.select_related('category').filter(stock__lt=5).order_by('stock')[:10]

        # Build extra context
        if extra_context is None:
            extra_context = {}

        extra_context.update({
            'orders_count': orders_count,
            'products_count': products_count,
            'customers_count': customers_count,
            'categories_count': categories_count,
            'recent_orders': recent_orders,
            'low_stock_products': low_stock_products,
        })

        return super().index(request, extra_context=extra_context)


# Create a custom admin site instance
audiolux_admin_site = AudioLuxAdminSite(name='audiolux_admin')

# Register models with the custom admin site
audiolux_admin_site.register(Category, CategoryAdmin)
audiolux_admin_site.register(Product, ProductAdmin)
audiolux_admin_site.register(Customer, CustomerAdmin)
audiolux_admin_site.register(Order, OrderAdmin)
audiolux_admin_site.register(OrderItem, OrderItemAdmin)
audiolux_admin_site.register(Cart, CartAdmin)
audiolux_admin_site.register(CartItem, CartItemAdmin)
