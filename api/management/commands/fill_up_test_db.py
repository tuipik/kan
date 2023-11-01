from datetime import datetime, timedelta
from random import choice, randint

from django.core.management.base import BaseCommand
from faker import Faker

from api.CONSTANTS import ROW_LATIN_LETTERS, CYRILLIC_LETTERS_UP
from api.models import (
    Status,
    BaseStatuses,
    User,
    Department,
    Task,
    TimeTracker,
    Comment, UserRoles,
)


class Command(BaseCommand):
    """Django command to fill up develop db"""

    fake = Faker('uk_UA')

    def create_user(self, dep, num, role):
        user = User.objects.create_user(
            username=f"user_{num}",
            first_name=self.fake.unique.first_name(),
            last_name=self.fake.unique.last_name(),
            password="qwerty",
            department=dep,
        )
        user.role = role
        user.save()
        self.stdout.write(f"Created user: {user.username}")
        return user

    def create_departments(self):
        deps = [
            ("ГІС", False),
            ("ВЕК", False),
            ("ВЦК", False),
            ("ВТК", True),
        ]
        user_counter = 1
        for dep in deps:

            department = Department.objects.create(name=dep[0], is_verifier=dep[1])
            department.save()
            user_1 = self.create_user(department, user_counter, role=UserRoles.EDITOR.value)
            user_counter += 1
            q = 4
            for i in range(q):
                role = UserRoles.EDITOR.value
                if dep[1]:
                    role = UserRoles.VERIFIER.value
                if not dep[1] and i == q-1:
                    role = UserRoles.CORRECTOR.value
                self.create_user(department, user_counter, role=role)
                user_counter += 1
            department.head = user_1
            department.save()
            self.stdout.write(f"Created department: {department.name}")

    def create_tasks(self):
        user_list = User.objects.filter(department__is_verifier=False)
        status = Status.objects.get_or_none(name=BaseStatuses.EDITING_QUEUE.value)
        names = []
        for department in Department.objects.filter(is_verifier=False):
            for user in [
                u
                for u in user_list
                if not u.is_head_department and u.department_id == department.id
            ]:
                for i in range(1, 4):
                    success = False
                    task_name = ""
                    while not success:
                        name = f"{choice(['K', 'L', 'M', 'N'])}-{randint(32, 38)}-{randint(1, 144)}-{choice(CYRILLIC_LETTERS_UP)}"
                        if name not in names:
                            names.append(name)
                            task_name = name
                            success = True

                    task = Task.objects.create(
                        **{
                            "name": task_name,
                            "editing_time_estimate": randint(16, 90),
                            "correcting_time_estimate": randint(16, 90),
                            "tc_time_estimate": randint(10, 90),
                            "quarter": randint(1, 2),
                            "category": randint(3, 10),
                            "user": user,
                            "department": department,
                            "year": datetime.today().year,
                            "status": status,
                            "scale": 50,
                        }
                    )
                    task.created = datetime.now() - timedelta(days=6)
                    task.save()

                    TimeTracker.objects.create(
                        task=task, user=User.objects.first(), task_status=status, task_department=task.department, start_time=task.created
                    )
                    Comment.objects.create(
                        task=task,
                        user=User.objects.first(),
                        body=f"Створено задачу {task.name}",
                        is_log=True,
                    )
                    self.stdout.write(f"Created task: {task.name}")

    def handle(self, *args, **options):
        self.stdout.write("Start fill up db")
        self.create_departments()
        self.create_tasks()
        self.stdout.write("Done")
