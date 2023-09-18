from sys import stdout

from api.models import Status, BaseStatuses


def fill_up_statuses(*args, **options):
    stdout.write('Start checking and adding statuses to db')
    counter = 0
    for status in BaseStatuses:
        instance, created = Status.objects.get_or_create(name=status.name, translation=status.value)
        if created:
            stdout.write(f'Added a new status: {status.name}')
            counter += 1
    if not counter:
        stdout.write(f'Any new status was added')
