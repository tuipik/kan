from datetime import datetime, timezone

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db import models


class UserManager(BaseUserManager):
    def create_user(
        self,
        username,
        first_name,
        last_name,
        password=None,
        department=None,
    ):
        if not username:
            raise ValueError("У користувача має бути унікальний логін")

        user = self.model(
            username=username,
            first_name=first_name,
            last_name=last_name,
            department=department,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        username,
        first_name,
        last_name,
        password=None,
        department=None,
    ):
        user = self.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            department=department,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=255, unique=True, verbose_name="Логін")
    first_name = models.CharField(max_length=255, verbose_name="Ім'я")
    last_name = models.CharField(max_length=255, verbose_name="Прізвище")
    department = models.ForeignKey(
        "Department",
        on_delete=models.SET_NULL,
        related_name="user_departments",
        verbose_name="Відділ",
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_head_department(self):
        if self.department and self.department.head.id == self.id:
            return True
        return False

    @property
    def is_staff(self):
        return self.is_admin


class Department(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Відділ")
    head = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        related_name="head_users",
        verbose_name="Керівник",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name


class YearQuarter(models.IntegerChoices):
    FIRST = 1, "Перший"
    SECOND = 2, "Другий"
    THIRD = 3, "Третій"
    FOURTH = 4, "Четвертий"


class TaskStatuses(models.TextChoices):
    WAITING = "WAITING", "Очікування"
    IN_PROGRESS = "IN_PROGRESS", "В роботі"
    STOPPED = "STOPPED", "Призупинено"
    DONE = "DONE", "Завершено"
    CORRECTING = "CORRECTING", "Корректура"
    CORRECTING_QUEUE = "CORRECTING_QUEUE", "Черга корректури"
    OTK = "OTK", "ОТК"
    OTK_QUEUE = "OTK_QUEUE", "Черга ОТК"


class Task(models.Model):
    name = models.CharField(max_length=255, verbose_name="Назва")
    change_time_estimate = models.PositiveIntegerField(
        default=0, verbose_name="Час на оновлення"
    )
    correct_time_estimate = models.PositiveIntegerField(
        default=0, verbose_name="Час на корегування"
    )
    otk_time_estimate = models.PositiveIntegerField(
        default=0, verbose_name="Час на ОТК"
    )
    status = models.CharField(
        max_length=50,
        choices=TaskStatuses.choices,
        default=TaskStatuses.WAITING,
        verbose_name="Статус",
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated = models.DateTimeField(auto_now=True, verbose_name="Оновлено")
    done = models.DateTimeField(blank=True, null=True, verbose_name="Завершено")
    quarter = models.IntegerField(
        choices=YearQuarter.choices, blank=True, verbose_name="Квартал"
    )
    category = models.CharField(max_length=255, verbose_name="Категорія")
    user = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        related_name="task_users",
        verbose_name="Відповідальний",
        blank=True,
        null=True,
    )
    department = models.ForeignKey(
        "Department",
        on_delete=models.SET_NULL,
        related_name="task_departments",
        verbose_name="Відділ",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name

    def start_time_tracker(self):
        data = {
            "task": self,
            "user": self.user,
            "status": TimeTrackerStatuses.IN_PROGRESS,
        }
        if TimeTracker.objects.filter(**data).count():
            return
        del data["status"]
        return TimeTracker.objects.create(**data)


class TimeTrackerStatuses(models.TextChoices):
    IN_PROGRESS = "IN_PROGRESS", "В роботі"
    DONE = "DONE", "Завершено"


class TimeTracker(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="time_tracker_tasks",
        verbose_name="Задача",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="time_tracker_users",
        verbose_name="Виконавець",
    )
    start_time = models.DateTimeField(verbose_name="Час початку", auto_now_add=True)
    end_time = models.DateTimeField(
        verbose_name="Час закінчення", null=True, blank=True
    )
    hours = models.IntegerField(verbose_name="Час виконання", default=0, blank=True)
    status = models.CharField(
        max_length=50,
        choices=TimeTrackerStatuses.choices,
        default=TimeTrackerStatuses.IN_PROGRESS,
        verbose_name="Статус",
    )

    def __str__(self):
        return f"{self.task.name} - {self.get_status_display()}"

    @property
    def max_hours_per_day(self) -> int:
        return 8  # робочий час не може бути більше 8 годин

    @property
    def rest_time(self) -> int:
        return 1

    @property
    def task_status(self):
        return self.task.status

    def change_status_done(self):
        time_now = datetime.now(timezone.utc)
        time_delta = round((time_now - self.start_time).total_seconds() / 60 / 60)
        if time_delta > self.max_hours_per_day:
            time_delta = self.max_hours_per_day
        elif time_delta > 4:
            time_delta -= self.rest_time  # віднімаємо годуну обіду
        self.end_time = time_now
        self.hours = time_delta
        self.status = TimeTrackerStatuses.DONE
        self.save()


class Comment(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="task_comments",
        verbose_name="Задача",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_comments",
        verbose_name="Виконавець",
    )
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created"]

    def __str__(self):
        return f"{self.user} commented {self.created}"
