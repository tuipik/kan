from django.core.management.base import BaseCommand

from api.models import Status, BaseStatuses
from api.utils import fill_up_statuses


class Command(BaseCommand):
    """Django command to fill up Status db table"""

    def handle(self, *args, **options):
        fill_up_statuses()
