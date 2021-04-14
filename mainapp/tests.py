from decimal import Decimal

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Category, Eva, CartProduct, Cart, Customer
from .views import recalc_cart

User = get_user_model()


class ShopTestCases(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(username='testuser', password='password')
        self.category = Category.objects.create(name='Eva-коврики', slug='eva')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        image = SimpleUploadedFile('small.gif', small_gif, content_type='image/gif')
        #image = SimpleUploadedFile('bosta_logo.jpg', content=b'', content_type='image/jpeg')
        self.eva = Eva.objects.create(
            category=self.category,
            title='Test Eva',
            slug='test-slug',
            image=image,
            price=Decimal('500.00'),
            size='20x10',
            color='red'
        ),
        self.customer = Customer.objects.create(user=self.user, phone='87777', address='some address')
        self.cart = Cart.objects.create(owner=self.customer)
        self.cart_product = CartProduct.objects.create(
            user=self.customer,
            cart=self.cart,
            content_object=self.eva
        )

    def test_add_to_cart(self):
        self.cart.products.add(self.cart_product)
        recalc_cart(self.cart)
        self.assertIn(self.cart_product, self.cart.products.all())
        self.assertEqual(self.cart.products.count(), 1)
        self.assertEqual(self.cart.final_price, Decimal('500.00'))

    def test_response_from_add_to_cart_view(self):
        client = Client()
        response = client.get('/add-to-cart/eva/test-slug/')
        self.assertEqual(response.status_code, 200)
