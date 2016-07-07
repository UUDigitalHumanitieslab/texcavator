from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Adds a guest User with the specified username and password in the settings file'

    def handle(self, *args, **options):
        try:
            get_user_model().objects.create_user(settings.GUEST_USERNAME, '', settings.GUEST_PASSWORD)
        except IntegrityError:
            print 'Guest user already exists, not added.'
        else:
            print 'Guest user created.'
