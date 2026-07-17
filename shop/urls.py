from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'shop'

urlpatterns = [
    # Home & Products
    path('', views.IndexView.as_view(), name='index'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    
    # Cart
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/<int:product_id>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.UpdateCartView.as_view(), name='update_cart'),
    
    # Checkout & Orders
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('order/confirmation/<int:order_id>/', views.OrderConfirmationView.as_view(), name='order_confirmation'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Admin Order Management
    path('admin-dashboard/orders/<int:pk>/', views.AdminOrderDetailView.as_view(), name='admin_order_detail'),
    path('admin-dashboard/orders/<int:pk>/update-status/', views.AdminOrderUpdateStatusView.as_view(), name='admin_order_update_status'),
    path('admin-dashboard/orders/export/csv/', views.AdminExportOrdersCSVView.as_view(), name='admin_export_orders_csv'),
    
    # Admin Customer Management
    path('admin-dashboard/customers/', views.AdminCustomerListView.as_view(), name='admin_customers'),
    path('admin-dashboard/customers/<int:pk>/', views.AdminCustomerDetailView.as_view(), name='admin_customer_detail'),
    path('admin-dashboard/customers/export/csv/', views.AdminExportCustomersCSVView.as_view(), name='admin_export_customers_csv'),
    
    # Admin Dashboard
    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin-dashboard/products/', views.AdminProductListView.as_view(), name='admin_products'),
    path('admin-dashboard/products/add/', views.AdminProductCreateView.as_view(), name='admin_product_add'),
    path('admin-dashboard/products/edit/<int:pk>/', views.AdminProductUpdateView.as_view(), name='admin_product_edit'),
    path('admin-dashboard/products/delete/<int:pk>/', views.AdminProductDeleteView.as_view(), name='admin_product_delete'),
    path('admin-dashboard/orders/', views.AdminOrderListView.as_view(), name='admin_orders'),
    path('admin-dashboard/categories/', views.AdminCategoryListView.as_view(), name='admin_categories'),
    path('admin-dashboard/categories/add/', views.AdminCategoryCreateView.as_view(), name='admin_category_add'),
    path('admin-dashboard/categories/edit/<int:pk>/', views.AdminCategoryUpdateView.as_view(), name='admin_category_edit'),
    path('admin-dashboard/categories/delete/<int:pk>/', views.AdminCategoryDeleteView.as_view(), name='admin_category_delete'),
]
