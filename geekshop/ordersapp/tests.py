from django.test import TestCase

from authapp.models import User
from mainapp.models import ProductCategory, Product
from ordersapp.models import Order, OrderItem
from django.test.client import Client


# Create your tests here.

class MainSmokeTest(TestCase):
    username = 'django1231'
    email = 'django@mail.ru'
    password = 'Geekshop123_'

    def setUp(self) -> None:
        self.user = User.objects.create_superuser(self.username, self.email, self.password)
        self.category = ProductCategory.objects.create(name='Test')
        self.product = Product.objects.create(category=self.category, name='product_1', price=100)
        self.order = Order.objects.create(user=self.user)
        self.orderitem = OrderItem.objects.create(order=self.order, product=self.product, quantity=1)

        self.client = Client()

    def test_order_update(self):
        # unregistered user is redirected, registered is allowed to update orders
        response = self.client.get('/orders/update/1/')
        self.assertEqual(response.status_code, 302)
        self.client.login(username=self.username, password=self.password)
        response = self.client.get('/orders/update/1/')
        self.assertTrue(self.user.is_active)
        self.assertEqual(response.status_code, 200)

    def tearDown(self) -> None:
        pass
