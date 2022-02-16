from django.conf import settings
from django.test import TestCase

from authapp.models import User
from django.test.client import Client


# Create your tests here.

class UserTestCase(TestCase):
    username = 'django1231'
    email = 'django@mail.ru'
    password = 'Geekshop123_'

    new_user_data = {
        'username': 'django1',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'django1@mail.ru',
        'password1': 'Geekshop1231_',
        'password2': 'Geekshop1231_',
        'age': 31,
    }

    def setUp(self) -> None:
        self.user = User.objects.create_superuser(self.username, self.email, self.password)
        self.client = Client()

    def test_profile_redirect(self):
        response = self.client.get('/users/profile/')
        self.assertEqual(response.status_code, 302)

    def test_login(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_anonymous)
        self.client.login(username=self.username, password=self.password)
        response = self.client.get('/users/login/')
        self.assertEqual(response.status_code, 200)

    def test_register(self):
        response = self.client.post('/users/register/', data=self.new_user_data)

        self.assertEqual(response.status_code, 302)

        user = User.objects.get(username=self.new_user_data['username'])
        activation_url = f"{settings.DOMAIN_NAME}/users/verify/{user.email}/{user.activation_key}/"

        response = self.client.get(activation_url)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(user.is_active)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def tearDown(self) -> None:
        pass
