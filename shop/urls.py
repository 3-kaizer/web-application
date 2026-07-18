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
]
