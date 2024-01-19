import os.path

from api.management.commands.task_importer.task_importer import TaskImporter
from django.core.management.base import BaseCommand

from kanban.settings import BASE_DIR


class Command(BaseCommand):
    """Django command to fill up develop db"""

    file = os.path.join(BASE_DIR, "task_updates_checked.xlsx")

    def handle(self, *args, **options):
        self.stdout.write("Start fill up db")
        task_importer = TaskImporter()
        task_importer.run(self.file)
        self.stdout.write("Done")