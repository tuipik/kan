from datetime import datetime
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
    Comment,
)


class Command(BaseCommand):
    """Django command to fill up develop db"""

    fake = Faker()

    def create_user(self, dep, num):
        user = User.objects.create_user(
            username=f"user_{num}",
            first_name=self.fake.unique.first_name(),
            last_name=self.fake.unique.last_name(),
            password="qwerty",
            department=dep,
        )
        self.stdout.write(f"Created user: {user.username}")
        return user

    def create_departments(self):
        deps = [
            ("Dep_1", False, [1, 2]),
            ("Dep_2", False, [1, 2]),
            ("Dep_3", False, [1, 2]),
            ("CORRECT", True, [3, 4]),
            ("VTK", True, [5, 6]),
        ]
        user_counter = 1
        for dep in deps:
            department = Department.objects.create(name=dep[0], is_verifier=dep[1])
            department.statuses.set(dep[2])
            department.save()
            user_1 = self.create_user(department, user_counter)
            user_counter += 1
            user_2 = self.create_user(department, user_counter)
            user_counter += 1
            department.head = user_1
            department.save()
            self.stdout.write(f"Created department: {department.name}")

    def create_tasks(self):
        user_list = User.objects.filter(department__is_verifier=False)
        status = Status.objects.get_or_none(name=BaseStatuses.WAITING.name)
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
                        name = f"{choice(ROW_LATIN_LETTERS)}-{randint(32, 38)}-{randint(1, 144)}-{choice(CYRILLIC_LETTERS_UP)}"
                        if name not in names:
                            names.append(name)
                            task_name = name
                            success = True

                    task = Task.objects.create(
                        **{
                            "name": task_name,
                            "change_time_estimate": randint(10, 90),
                            "correct_time_estimate": randint(10, 90),
                            "otk_time_estimate": randint(10, 90),
                            "quarter": 1,
                            "category": self.fake.sentence(nb_words=6),
                            "user": user,
                            "department": department,
                            "primary_department": department,
                            "year": datetime.today().year,
                            "status": status,
                            "scale": 50,
                        }
                    )

                    TimeTracker.objects.create(
                        task=task, user=User.objects.first(), task_status=status
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
