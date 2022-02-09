from django.core.management.base import BaseCommand

from authapp.models import User
from authapp.models import UserProfile


class Command(BaseCommand):
    def handle(self, *args, **options):
        for user in User.objects.filter(userprofile__isnull=True):
            UserProfile.objects.create(user=user)
