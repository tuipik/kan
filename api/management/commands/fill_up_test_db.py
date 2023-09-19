from django.core.management.base import BaseCommand

from api.models import Status, BaseStatuses, User, Department, Task, TimeTracker, Comment, UserManager


class Command(BaseCommand):
    """Django command to fill up develop db"""
    def create_user(self, dep, num):
        return User.objects.create_user(
            username=f"user_{dep.name}_{num}",
            first_name=f"First_name_{dep.name}_{num}",
            last_name=f"Last_name_{dep.name}_{num}",
            password="qwerty",
            department=dep,
        )

    def create_departments(self):
        deps = [
            ("Dep_1", False, [1, 2]),
            ("CORRECT", True, [3, 4]),
            ("VTK", True, [5, 6]),
        ]
        for dep in deps:
            department = Department.objects.create(name=dep[0], is_verifier=dep[1])
            department.statuses.set(dep[2])
            department.save()
            user_1 = self.create_user(department, 1)
            user_2 = self.create_user(department, 2)
            department.head = user_1
            department.save()

    def create_tasks(self):
        user = User.objects.filter(department__name='Dep_1').last()
        status = Status.objects.get(name=BaseStatuses.WAITING.name)
        for i in range(1, 4):
            task = Task.objects.create(
                **{
                    "name": f"M-36-10{i}-A",
                    "change_time_estimate": 55 + i,
                    "correct_time_estimate": 54 + i,
                    "otk_time_estimate": 53 + i,
                    "quarter": 1,
                    "category": "some_cat",
                    "user": user,
                    "department": Department.objects.get(name="Dep_1"),
                    "year": 2023,
                    "status": status
                }
            )
            TimeTracker.objects.create(
                task=task,
                user=User.objects.first(),
                task_status=status
            )
            Comment.objects.create(
                task=task,
                user=User.objects.first(),
                body=f"Створено задачу {task.name}",
                is_log=True
            )

    def handle(self, *args, **options):
        self.stdout.write("Start fill up db")
        self.create_departments()
        self.create_tasks()
