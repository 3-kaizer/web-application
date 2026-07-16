from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Category, Product, Order


class CartAndCheckoutTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Over-Ear', slug='over-ear')
        self.product = Product.objects.create(
            name='Demo Headphones',
            slug='demo-headphones',
            category=self.category,
            description='A reliable demo headset.',
            specifications='Battery Life: 20 hours\nConnectivity: Bluetooth 5.3',
            price=Decimal('199.99'),
            stock=10,
            is_available=True,
        )

    def test_cart_view_renders_with_decimal_totals(self):
        self.client.post(
            reverse('shop:add_to_cart', args=[self.product.pk]),
            data={'next': '/cart/'},
        )

        response = self.client.get(reverse('shop:cart'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['subtotal'], Decimal('199.99'))
        self.assertEqual(response.context['tax'], Decimal('15.9992'))
        self.assertEqual(response.context['total'], Decimal('215.9892'))

    def test_guest_checkout_creates_order_without_login(self):
        self.client.post(
            reverse('shop:add_to_cart', args=[self.product.pk]),
            data={'next': '/checkout/'},
        )

        response = self.client.post(
            reverse('shop:checkout'),
            data={
                'first_name': 'Ada',
                'last_name': 'Lovelace',
                'email': 'ada@example.com',
                'phone': '0712345678',
                'address': '123 Test Street',
                'city': 'Nairobi',
                'postal_code': '00100',
                'country': 'Kenya',
                'payment_method': 'paypal',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Order.objects.exists())
        self.assertEqual(Order.objects.first().payment_status, 'completed')
