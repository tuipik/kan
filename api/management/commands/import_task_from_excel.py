from api.management.commands.task_importer.task_importer import TaskImporter
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to fill up develop db"""

    file = "/home/yurii/PROJECTS/kan/api/management/commands/task_importer/task_updates_checked.xlsx"

    def handle(self, *args, **options):
        self.stdout.write("Start fill up db")
        task_importer = TaskImporter()
        task_importer.run(self.file)
        self.stdout.write("Done")