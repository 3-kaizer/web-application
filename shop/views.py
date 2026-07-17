from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.db.models import Q, Sum, Count
from django.conf import settings
from django.urls import reverse_lazy
from decimal import Decimal
import json
import uuid

from .models import Category, Product, Cart, CartItem, Order, OrderItem, Customer
from .forms import CustomerRegistrationForm


def calculate_totals(subtotal):
    shipping = Decimal('0.00')
    tax_rate = Decimal('0.08')
    tax = subtotal * tax_rate
    total = subtotal + shipping + tax
    return subtotal, shipping, tax, total


# =============================================
# Authentication Views
# =============================================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('shop:index')

    next_url = request.POST.get('next') or request.GET.get('next') or ''

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Merge cart from session to user
            session_id = request.session.session_key
            if session_id:
                try:
                    guest_cart = Cart.objects.get(session_id=session_id)
                    user_cart, created = Cart.objects.get_or_create(user=user)
                    for item in guest_cart.items.all():
                        user_cart_item, created = CartItem.objects.get_or_create(
                            cart=user_cart,
                            product=item.product,
                            defaults={'quantity': item.quantity}
                        )
                        if not created:
                            user_cart_item.quantity += item.quantity
                            user_cart_item.save()
                    guest_cart.delete()
                except Cart.DoesNotExist:
                    pass
            messages.success(request, f'Welcome back, {user.username}!')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('shop:index')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('shop:index')
    
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {user.username}.')
            return redirect('shop:index')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('shop:index')


# =============================================
# Product & Category Views
# =============================================

class IndexView(ListView):
    model = Product
    template_name = 'index.html'
    context_object_name = 'products'
    paginate_by = 8

    def get_queryset(self):
        queryset = Product.objects.filter(is_available=True)
        category_slug = self.request.GET.get('category')
        search_query = self.request.GET.get('search')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search_query'] = self.request.GET.get('search', '').strip()
        context['selected_category'] = self.request.GET.get('category', '')
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.filter(is_available=True)


class CategoryView(ListView):
    model = Product
    template_name = 'index.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(category__slug=self.kwargs['slug'], is_available=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


# =============================================
# Cart Views
# =============================================

class CartView(View):
    def get(self, request):
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            session_id = request.session.session_key
            if not session_id:
                request.session.create()
                session_id = request.session.session_key
            cart, created = Cart.objects.get_or_create(session_id=session_id)
        
        cart_items = cart.items.select_related('product').all()
        subtotal = cart.total_price
        subtotal, shipping, tax, total = calculate_totals(subtotal)
        
        context = {
            'cart': cart,
            'cart_items': cart_items,
            'subtotal': subtotal,
            'shipping': shipping,
            'tax': tax,
            'total': total,
        }
        return render(request, 'cart.html', context)


class AddToCartView(View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, is_available=True)
        try:
            quantity = max(1, int(request.POST.get('quantity', 1)))
        except (TypeError, ValueError):
            quantity = 1

        if product.stock < 1:
            messages.warning(request, f'{product.name} is currently out of stock.')
            return redirect(request.POST.get('next', 'shop:index'))

        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            session_id = request.session.session_key
            if not session_id:
                request.session.create()
                session_id = request.session.session_key
            cart, created = Cart.objects.get_or_create(session_id=session_id)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 0}
        )
        cart_item.quantity += quantity
        if cart_item.quantity > product.stock:
            cart_item.quantity = product.stock
            messages.warning(request, f'Only {product.stock} items available. Adjusted quantity.')
        cart_item.save()

        messages.success(request, f'{product.name} added to cart!')
        next_url = request.POST.get('next', 'shop:cart')
        return redirect(next_url)


class RemoveFromCartView(View):
    def post(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id)
        
        if request.user.is_authenticated:
            if cart_item.cart.user != request.user:
                messages.error(request, 'Unauthorized action.')
                return redirect('shop:cart')
        else:
            session_id = request.session.session_key
            if cart_item.cart.session_id != session_id:
                messages.error(request, 'Unauthorized action.')
                return redirect('shop:cart')
        
        product_name = cart_item.product.name
        cart_item.delete()
        messages.success(request, f'{product_name} removed from cart.')
        return redirect('shop:cart')


class UpdateCartView(View):
    def post(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id)
        action = request.POST.get('action')

        if request.user.is_authenticated:
            if cart_item.cart.user != request.user:
                messages.error(request, 'Unauthorized action.')
                return redirect('shop:cart')
        else:
            session_id = request.session.session_key
            if cart_item.cart.session_id != session_id:
                messages.error(request, 'Unauthorized action.')
                return redirect('shop:cart')

        if action == 'increase':
            if cart_item.quantity < cart_item.product.stock:
                cart_item.quantity += 1
                cart_item.save()
            else:
                messages.warning(request, 'Maximum stock reached.')
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
                messages.info(request, 'Item removed from cart (quantity reached 0).')
        
        return redirect('shop:cart')


# =============================================
# Checkout & Payment Views
# =============================================

class CheckoutView(View):
    def get(self, request):
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            session_id = request.session.session_key
            cart = Cart.objects.filter(session_id=session_id).first()
        
        if not cart or cart.items.count() == 0:
            messages.warning(request, 'Your cart is empty.')
            return redirect('shop:index')

        cart_items = cart.items.select_related('product').all()
        subtotal = cart.total_price
        subtotal, shipping, tax, total = calculate_totals(subtotal)
        
        context = {
            'cart': cart,
            'cart_items': cart_items,
            'subtotal': subtotal,
            'shipping': shipping,
            'tax': tax,
            'total': total,
        }
        return render(request, 'checkout.html', context)

    def post(self, request):
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            session_id = request.session.session_key
            cart = Cart.objects.filter(session_id=session_id).first()

        if not cart or cart.items.count() == 0:
            messages.warning(request, 'Your cart is empty.')
            return redirect('shop:index')

        # Get shipping details
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')
        payment_method = request.POST.get('payment_method')

        if not all([first_name, last_name, email, phone, address, city, postal_code, country, payment_method]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('shop:checkout')

        if payment_method not in ['paypal', 'mastercard']:
            messages.error(request, 'Invalid payment method selected.')
            return redirect('shop:checkout')

        # Calculate total
        subtotal = cart.total_price
        subtotal, _, _, total_amount = calculate_totals(subtotal)

        # Simulate payment processing
        payment_status = 'completed'
        transaction_id = None

        if payment_method == 'paypal':
            transaction_id = f"PAYPAL-{uuid.uuid4().hex.upper()}"
        elif payment_method == 'mastercard':
            # Simulate MasterCard charge
            card_number = request.POST.get('card_number', '').replace(' ', '')
            expiry = request.POST.get('expiry', '')
            cvv = request.POST.get('cvv', '')
            
            if not card_number or not expiry or not cvv:
                messages.error(request, 'Please provide all credit card details.')
                return redirect('shop:checkout')
            
            # Basic validation simulation
            if len(card_number.replace(' ', '')) < 16:
                messages.error(request, 'Invalid card number.')
                return redirect('shop:checkout')
            
            transaction_id = f"MC-{uuid.uuid4().hex.upper()}"

        # Create order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_id=request.session.session_key,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            postal_code=postal_code,
            country=country,
            payment_method=payment_method,
            payment_status=payment_status,
            transaction_id=transaction_id,
            total_amount=total_amount,
        )

        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
            )
            # Update stock
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()

        # Clear cart
        cart.items.all().delete()

        messages.success(request, f'Order #{order.id} placed successfully! Thank you for your purchase.')
        return redirect('shop:order_confirmation', order_id=order.id)


class OrderConfirmationView(View):
    def get(self, request, order_id):
        if request.user.is_authenticated:
            order = get_object_or_404(Order, id=order_id, user=request.user)
        else:
            session_id = request.session.session_key
            order = get_object_or_404(Order, id=order_id, session_id=session_id)
        
        return render(request, 'order_confirmation.html', {'order': order})


# =============================================
# Admin Dashboard Views
# =============================================

def is_admin(user):
    """Check if user is the superuser/admin"""
    return user.is_authenticated and user.is_superuser


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_admin(self.request.user)


class AdminDashboardView(AdminRequiredMixin, View):
    def get(self, request):
        total_products = Product.objects.count()
        total_orders = Order.objects.count()
        total_revenue = Order.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_customers = Customer.objects.count()
        low_stock_products = Product.objects.filter(stock__lt=5, is_available=True)
        recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
        category_stats = Category.objects.annotate(
            product_count=Count('products')
        ).order_by('-product_count')[:5]

        context = {
            'total_products': total_products,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'total_customers': total_customers,
            'low_stock_products': low_stock_products,
            'recent_orders': recent_orders,
            'category_stats': category_stats,
        }
        return render(request, 'admin/dashboard.html', context)


# =============================================
# Admin Product Views
# =============================================

class AdminProductListView(AdminRequiredMixin, ListView):
    model = Product
    template_name = 'admin/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        queryset = Product.objects.select_related('category').all()
        search_query = self.request.GET.get('search')
        category_filter = self.request.GET.get('category')
        availability_filter = self.request.GET.get('availability')

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )
        if category_filter:
            queryset = queryset.filter(category__slug=category_filter)
        if availability_filter:
            queryset = queryset.filter(is_available=(availability_filter == 'available'))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_availability'] = self.request.GET.get('availability', '')
        return context


class AdminProductCreateView(AdminRequiredMixin, CreateView):
    model = Product
    template_name = 'admin/product_form.html'
    fields = ['name', 'category', 'description', 'specifications', 'price', 'stock', 'is_available', 'image']
    success_url = reverse_lazy('shop:admin_products')

    def form_valid(self, form):
        messages.success(self.request, f'Product "{form.instance.name}" created successfully!')
        return super().form_valid(form)


class AdminProductUpdateView(AdminRequiredMixin, UpdateView):
    model = Product
    template_name = 'admin/product_form.html'
    fields = ['name', 'category', 'description', 'specifications', 'price', 'stock', 'is_available', 'image']
    success_url = reverse_lazy('shop:admin_products')

    def form_valid(self, form):
        messages.success(self.request, f'Product "{form.instance.name}" updated successfully!')
        return super().form_valid(form)


class AdminProductDeleteView(AdminRequiredMixin, DeleteView):
    model = Product
    template_name = 'admin/product_confirm_delete.html'
    success_url = reverse_lazy('shop:admin_products')

    def delete(self, request, *args, **kwargs):
        product_name = self.get_object().name
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return response


# =============================================
# Admin Order Views
# =============================================

class AdminOrderListView(AdminRequiredMixin, ListView):
    model = Order
    template_name = 'admin/order_list.html'
    context_object_name = 'orders'
    paginate_by = 25

    def get_queryset(self):
        queryset = Order.objects.select_related('user').prefetch_related('items__product').all()
        payment_status = self.request.GET.get('payment_status')
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payment_status_choices'] = Order.PAYMENT_STATUS_CHOICES
        context['selected_status'] = self.request.GET.get('payment_status', '')
        return context


# =============================================
# Admin Category Views
# =============================================

class AdminCategoryListView(AdminRequiredMixin, ListView):
    model = Category
    template_name = 'admin/category_list.html'
    context_object_name = 'categories'
    paginate_by = 50

    def get_queryset(self):
        return Category.objects.annotate(product_count=Count('products')).order_by('name')


class AdminCategoryCreateView(AdminRequiredMixin, CreateView):
    model = Category
    template_name = 'admin/category_form.html'
    fields = ['name']
    success_url = reverse_lazy('shop:admin_categories')

    def form_valid(self, form):
        messages.success(self.request, f'Category "{form.instance.name}" created successfully!')
        return super().form_valid(form)


class AdminCategoryUpdateView(AdminRequiredMixin, UpdateView):
    model = Category
    template_name = 'admin/category_form.html'
    fields = ['name']
    success_url = reverse_lazy('shop:admin_categories')

    def form_valid(self, form):
        messages.success(self.request, f'Category "{form.instance.name}" updated successfully!')
        return super().form_valid(form)


class AdminCategoryDeleteView(AdminRequiredMixin, DeleteView):
    model = Category
    template_name = 'admin/category_confirm_delete.html'
    success_url = reverse_lazy('shop:admin_categories')

    def delete(self, request, *args, **kwargs):
        category_name = self.get_object().name
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Category "{category_name}" deleted successfully!')
        return response


# =============================================
# Admin Order Detail View
# =============================================

class AdminOrderDetailView(AdminRequiredMixin, DetailView):
    model = Order
    template_name = 'admin/order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payment_status_choices'] = Order.PAYMENT_STATUS_CHOICES
        return context


class AdminOrderUpdateStatusView(AdminRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        new_status = request.POST.get('payment_status')
        
        if new_status in dict(Order.PAYMENT_STATUS_CHOICES):
            old_status = order.get_payment_status_display()
            order.payment_status = new_status
            order.save()
            messages.success(request, f'Order #{order.id} status updated from {old_status} to {order.get_payment_status_display()}.')
        else:
            messages.error(request, 'Invalid status selected.')
        
        return redirect('shop:admin_order_detail', pk=order.pk)


# =============================================
# Admin Customer Views
# =============================================

class AdminCustomerListView(AdminRequiredMixin, ListView):
    model = Customer
    template_name = 'admin/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 25

    def get_queryset(self):
        queryset = Customer.objects.select_related('user').all()
        search_query = self.request.GET.get('search')
        
        if search_query:
            queryset = queryset.filter(
                Q(user__username__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(city__icontains=search_query)
            )
        
        return queryset.order_by('-date_registered')


class AdminCustomerDetailView(AdminRequiredMixin, DetailView):
    model = Customer
    template_name = 'admin/customer_detail.html'
    context_object_name = 'customer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.get_object()
        context['orders'] = Order.objects.filter(user=customer.user).order_by('-created_at')[:10]
        context['total_orders'] = Order.objects.filter(user=customer.user).count()
        context['total_spent'] = Order.objects.filter(user=customer.user).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        return context


# =============================================
# CSV Export Views
# =============================================

class AdminExportOrdersCSVView(AdminRequiredMixin, View):
    def get(self, request):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Order ID', 'Customer', 'Email', 'Phone', 'Payment Method', 
            'Payment Status', 'Transaction ID', 'Total Amount', 'Date'
        ])
        
        orders = Order.objects.select_related('user').all().order_by('-created_at')
        
        for order in orders:
            customer_name = order.user.username if order.user else f"{order.first_name} {order.last_name}"
            writer.writerow([
                order.id,
                customer_name,
                order.email,
                order.phone,
                order.get_payment_method_display(),
                order.get_payment_status_display(),
                order.transaction_id or '',
                order.total_amount,
                order.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response


class AdminExportCustomersCSVView(AdminRequiredMixin, View):
    def get(self, request):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="customers_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Username', 'Email', 'Phone', 'Address', 'City', 
            'Postal Code', 'Country', 'Date Registered'
        ])
        
        customers = Customer.objects.select_related('user').all().order_by('-date_registered')
        
        for customer in customers:
            writer.writerow([
                customer.user.username,
                customer.email,
                customer.phone or '',
                customer.address or '',
                customer.city or '',
                customer.postal_code or '',
                customer.country or '',
                customer.date_registered.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
