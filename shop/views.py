from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.conf import settings
import json
import uuid

from .models import Category, Product, Cart, CartItem, Order, OrderItem


# =============================================
# Authentication Views
# =============================================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('shop:index')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
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
                messages.success(request, f'Welcome back, {username}!')
                return redirect('shop:index')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('shop:index')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {user.username}.')
            return redirect('shop:index')
    else:
        form = UserCreationForm()
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
        shipping = 0
        tax = subtotal * 0.08
        total = subtotal + shipping + tax
        
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

@method_decorator(login_required, name='dispatch')
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
        shipping = 0
        tax = subtotal * 0.08
        total = subtotal + shipping + tax
        
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
        total_amount = subtotal + (subtotal * 0.08)

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
