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
    name = models.CharField(max_length=255, verbose_name="Відділ")
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


class Task(models.Model):
    class YearQuarter(models.IntegerChoices):
        FIRST = 1, "Перший"
        SECOND = 2, "Другий"
        THIRD = 3, "Третій"
        FOURTH = 4, "Четвертий"

    class Statuses(models.TextChoices):
        WAITING = "WAITING", "Очікування"
        IN_PROGRESS = "IN_PROGRESS", "В роботі"
        STOPPED = "STOPPED", "Призупинено"
        DONE = "DONE", "Завершено"
        CORRECTING = "CORRECTING", "Корректура"
        CORRECTING_QUEUE = "CORRECTING_QUEUE", "Черга корректури"
        OTK = "OTK", "ОТК"
        OTK_QUEUE = "OTK_QUEUE", "Черга ОТК"

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
        choices=Statuses.choices,
        default=Statuses.WAITING,
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


class TimeTracker(models.Model):
    class Statuses(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", "В роботі"
        STOPPED = "STOPPED", "Призупинено"
        CANCELED = "CANCELED", "Відмінено"
        DONE = "DONE", "Завершено"

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='time_tracker_tasks', verbose_name='Задача')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_tracker_users', verbose_name='Виконавець')
    start_time = models.DateTimeField(verbose_name='Час початку', auto_now_add=True)
    end_time = models.DateTimeField(verbose_name='Час закінчення', null=True, blank=True)
    hours = models.IntegerField(verbose_name='Час виконання', default=0, blank=True)
    status = models.CharField(
        max_length=50,
        choices=Statuses.choices,
        default=Statuses.IN_PROGRESS,
        verbose_name="Статус",
    )

    def __str__(self):
        return f'{self.task.name} - {self.get_status_display()}'


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_comments', verbose_name='Задача')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments', verbose_name='Виконавець')
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return f'{self.user} commented {self.created}'
