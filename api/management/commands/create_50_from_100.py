from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from api.CONSTANTS import TRAPEZE_500K_AND_50K_CHOICES

from api.models import (
    Statuses,
    User,
    Task,
    TimeTracker,
    Comment,
)


class Command(BaseCommand):
    """Django command to fill up develop db"""

    def create_50_tasks_from_100_tasks(self):

        tasks_100_list = Task.objects.filter(scale=100)
        for task_100 in tasks_100_list:
            for letter in TRAPEZE_500K_AND_50K_CHOICES:
                task = Task.objects.create(
                    **{
                        "name": f"{task_100.name}-{letter}",
                        "editing_time_estimate": 5,
                        "correcting_time_estimate": 0,
                        "tc_time_estimate": 3,
                        "quarter": 1,
                        "category": 8,
                        "department": task_100.department,
                        "year": datetime.today().year,
                        "status": Statuses.EDITING_QUEUE.value,
                        "scale": 50,
                    }
                )
                task.save()

                TimeTracker.objects.create(
                    task=task,
                    task_status=Statuses.EDITING_QUEUE.value,
                    task_department=task.department,
                    start_time=task.created,
                )
                Comment.objects.create(
                    task=task,
                    user=User.objects.first(),
                    body=f"Створено задачу {task.name}",
                    is_log=True,
                )
                self.stdout.write(f"Created task: {task.name}")

    def handle(self, *args, **options):
        self.stdout.write("Starting creating 50k tasks")
        self.create_50_tasks_from_100_tasks()
        self.stdout.write("Done")

