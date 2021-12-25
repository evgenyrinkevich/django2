from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse

from django.utils.timezone import now

from geekshop.settings import ACTIVATION_KEY_TTL


class User(AbstractUser):
    image = models.ImageField(upload_to='users_image', blank=True)
    age = models.PositiveIntegerField(default=18)
    activation_key = models.CharField(max_length=128, blank=True)

    def is_activation_key_expired(self):
        return now() - self.date_joined > timedelta(hours=ACTIVATION_KEY_TTL)

    def send_verify_mail(self):
        verify_link = reverse('authapp:verify', kwargs={'email': self.email,
                                                        'activation_key': self.activation_key})

        subject = f'Confirm {self.username}'
        message = f'To confirm {self.username} on web-site ' \
                  f'{settings.DOMAIN_NAME} click: \n{settings.DOMAIN_NAME}{verify_link} '

        return send_mail(subject, message, settings.EMAIL_HOST_USER, [self.email], fail_silently=False)
