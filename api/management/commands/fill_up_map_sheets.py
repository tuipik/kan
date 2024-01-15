from django.core.management.base import BaseCommand

from api.models import (
    Task,
)
from api.serializers import MapSheetSerializer


class Command(BaseCommand):
    """Django command to fill up Tasks with nullable map_sheet"""

    @staticmethod
    def create_map_sheets():

        tasks_without_map_sheets = Task.objects.filter(map_sheet=None)

        map_sheets_count = 0
        for task in tasks_without_map_sheets:
            map_sheet_data = {
                'name': task.name,
                'scale': task.scale,
                'year': task.year,
            }

            map_sheet_serializer = MapSheetSerializer(data=map_sheet_data)
            map_sheet_serializer.is_valid(raise_exception=True)
            map_sheet = map_sheet_serializer.save()
            task.map_sheet = map_sheet
            task.save()
            print(f"{map_sheet} created")
            map_sheets_count += 1

        print(f"Created {map_sheets_count} MapSheets")

    def handle(self, *args, **options):
        self.stdout.write("Starting creating map sheets...")
        self.create_map_sheets()
        self.stdout.write("Done")
