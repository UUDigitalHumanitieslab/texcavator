from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from query.models import Query, StopWord


class Command(BaseCommand):
    help = 'Deletes all data of the guest User'

    def handle(self, *args, **options):
        guest_user = get_user_model().objects.get(username=settings.GUEST_USERNAME)

        StopWord.objects.filter(user=guest_user).delete()
        Query.objects.filter(user=guest_user).delete()
