from datetime import datetime, timezone

from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.db import models
from django.db.models import Sum

from kanban.settings import business_hours


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


class User(AbstractBaseUser, PermissionsMixin):
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
        return f"<User {self.last_name} {self.first_name}>"

    @property
    def is_head_department(self):
        if self.department and self.department.head.id == self.id:
            return True
        return False

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_superuser(self):
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
    is_verifier = models.BooleanField(default=False, verbose_name="Перевіряючий відділ")

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
        on_delete=models.PROTECT,
        related_name="task_departments",
        verbose_name="Відділ",
    )

    def __str__(self):
        return self.name

    @property
    def change_time_done(self):
        hours_sum = self.time_tracker_tasks.filter(
            task_status=TaskStatuses.IN_PROGRESS
        ).aggregate(total_hours=Sum("hours"))
        return hours_sum.get("total_hours", 0) or 0

    @property
    def correct_time_done(self):
        hours_sum = self.time_tracker_tasks.filter(
            task_status=TaskStatuses.CORRECTING
        ).aggregate(total_hours=Sum("hours"))
        return hours_sum.get("total_hours", 0) or 0

    @property
    def otk_time_done(self):
        hours_sum = self.time_tracker_tasks.filter(
            task_status=TaskStatuses.OTK
        ).aggregate(total_hours=Sum("hours"))
        return hours_sum.get("total_hours", 0) or 0

    def start_time_tracker(self):
        data = {
            "task": self,
            "user": self.user,
            "status": TimeTrackerStatuses.IN_PROGRESS,
            "task_status": self.status,
        }
        if not TimeTracker.objects.filter(**data).count():
            del data["status"]
            return TimeTracker.objects.create(**data)

    def create_log_comment(self, log_user, log_text, is_log):
        return Comment.objects.create(
            task=self, user=log_user, body=log_text, is_log=is_log
        )


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
        null=True,
        blank=True,
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
    task_status = models.CharField(
        max_length=50,
        choices=TaskStatuses.choices,
        default=TaskStatuses.WAITING,
        blank=True,
        verbose_name="Статус задачі",
    )

    def __str__(self):
        return f"{self.task.name} - {self.get_status_display()}"

    def change_status_done(self):
        self.end_time = datetime.now(timezone.utc)
        self.status = TimeTrackerStatuses.DONE
        self.save()

    def save(self, *args, **kwargs):
        time_now = self.end_time or datetime.now(timezone.utc)
        if self.start_time:
            self.hours = business_hours.difference(self.start_time, time_now).hours
        super(TimeTracker, self).save(*args, **kwargs)


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
        null=True,
        blank=True,
    )
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_log = models.BooleanField(default=False)

    class Meta:
        ordering = ["created"]

    def __str__(self):
        return f"{self.user} commented {self.created}"
