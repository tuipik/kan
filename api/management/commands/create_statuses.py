from django.core.management.base import BaseCommand

from api.models import Status, BaseStatuses


class Command(BaseCommand):
    """Django command to fill up Status db table"""

    def handle(self, *args, **options):
        self.stdout.write('Start checking and adding statuses to db')
        counter = 0
        for status in BaseStatuses:
            instance, created = Status.objects.get_or_create(name=status.name, translation=status.value)
            if created:
                self.stdout.write(f'Added a new status: {status.name}')
                counter += 1
        if not counter:
            self.stdout.write(f'Any new status was added')
