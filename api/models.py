from datetime import datetime, date

import regex
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.db.models import Sum, F
from rest_framework.exceptions import ValidationError

from api.CONSTANTS import TASK_NAME_REGEX, TASK_NAME_RULES
from api.fields import RangeIntegerField
from kanban.settings import business_hours

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.base import ModelBase
from django.db.models.manager import Manager


class GetObjectManager(Manager):
    def get_or_none(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except ObjectDoesNotExist:
            return None


class MetaModelBase(ModelBase):
    def _prepare(cls):
        manager = GetObjectManager()
        manager.auto_created = True
        cls.add_to_class("objects", manager)

        super()._prepare()

    class Meta:
        abstract = True


class UpdatedModel(models.Model, metaclass=MetaModelBase):
    managers = False

    class Meta:
        abstract = True

    @classmethod
    def get_field_names(cls):
        return [f.name for f in cls._meta.fields]


class UserManager(BaseUserManager, GetObjectManager):
    def create_user(
        self,
        username,
        first_name,
        last_name,
        password=None,
        department=None,
    ):
        if not username:
            raise ValidationError({"login": "У користувача має бути унікальний логін"})

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


class UserRoles(models.TextChoices):
    EDITOR = "EDITOR", "Виконавець"
    CORRECTOR = "CORRECTOR", "Коректувальник"
    VERIFIER = "VERIFIER", "Контролер"


class User(AbstractBaseUser, UpdatedModel, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True, verbose_name="Логін")
    first_name = models.CharField(max_length=255, verbose_name="Ім'я")
    last_name = models.CharField(max_length=255, verbose_name="Прізвище")
    department = models.ForeignKey(
        "Department",
        on_delete=models.SET_NULL,
        related_name="users",
        verbose_name="Відділ",
        blank=True,
        null=True,
    )
    role = models.CharField(
        max_length=32,
        choices=UserRoles.choices,
        default=UserRoles.EDITOR,
        verbose_name="Роль",
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

    def can_be_set_as_task_user(self, status, request_user):
        if status in [
            Statuses.EDITING_QUEUE.value,
            Statuses.EDITING.value,
        ] and self.role not in [UserRoles.EDITOR.value, UserRoles.CORRECTOR.value]:
            raise ValidationError(
                {
                    "status": f"Для статусу '{Statuses[status].label}' не можна призначити користувача, роль якого '{UserRoles[self.role].label}'."
                }
            )

        if status in [
            Statuses.CORRECTING_QUEUE.value,
            Statuses.CORRECTING.value,
        ] and self.role != UserRoles.CORRECTOR.value:
            raise ValidationError(
                {
                    "status": f"Для статусу '{Statuses[status].label}' можна призначити тільки користувача роль, якого '{UserRoles.CORRECTOR.label}'."
                }
            )

        if status in [
            Statuses.TC_QUEUE.value,
            Statuses.TC.value,
        ] and self.role != UserRoles.VERIFIER.value:
            raise ValidationError(
                {
                    "status": f"Для статусу '{Statuses[status].label}' можна призначити тільки користувача роль, якого '{UserRoles.VERIFIER.label}'."
                }
            )
        if not status and (not request_user.is_admin or request_user.is_head_department):
            raise ValidationError(
                {
                    "user": f"Тільки Адміністратор або Керівник віддулу може змінювати виконавця задачі."
                }
            )


    def can_change_task_status(self, status):
        if (
            not self.is_admin
            and self.role == UserRoles.EDITOR.value
            and status not in Statuses.EDITORS_STATUSES()
        ):
            raise ValidationError(
                {
                    "status": "Виконавець може змінити статус задачі тільки на 'Черга редагування', 'Редагування', 'Черга коректування'."
                }
            )

        if (
            not self.is_admin
            and self.role == UserRoles.CORRECTOR.value
            and status not in Statuses.CORRECTORS_STATUSES()
        ):
            raise ValidationError(
                {
                    "status": "Коректувальник не може змінити статус задачі на 'Технічний контроль' та 'Завершено'."
                }
            )

        if (
            not self.is_admin
            and self.role == UserRoles.VERIFIER.value
            and status not in Statuses.VERIFIERS_STATUSES()
        ):
            raise ValidationError(
                {
                    "status": "Контролер не може змінити статус задачі на 'Редагування' та 'Коректування'."
                }
            )


class Department(UpdatedModel):
    name = models.CharField(max_length=255, unique=True, verbose_name="Відділ")
    head = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        related_name="deparment_head",
        verbose_name="Керівник",
        blank=True,
        null=True,
    )
    is_verifier = models.BooleanField(default=False, verbose_name="Перевіряючий відділ")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["is_verifier", "id"]


class YearQuarter(models.IntegerChoices):
    FIRST = 1, "Перший"
    SECOND = 2, "Другий"
    THIRD = 3, "Третій"
    FOURTH = 4, "Четвертий"


class TaskScales(models.IntegerChoices):
    TWENTY_FIVE = 25, "1:25 000"
    FIFTY = 50, "1:50 000"
    ONE_HUNDRED = 100, "1:100 000"
    TWO_HUNDRED = 200, "1:200 000"
    FIVE_HUNDRED = 500, "1:500 000"


class Statuses(models.TextChoices):
    EDITING_QUEUE = "EDITING_QUEUE", "Черга редагування"
    EDITING = "EDITING", "Редагування"
    CORRECTING_QUEUE = "CORRECTING_QUEUE", "Черга коректування"
    CORRECTING = "CORRECTING", "Коректування"
    TC_QUEUE = "TC_QUEUE", "Черга технічного контролю"
    TC = "TC", "Технічний контроль"
    DONE = "DONE", "Завершено"

    @classmethod
    def STATUSES_PROGRESS(cls) -> list:
        return [Statuses.EDITING.value, Statuses.CORRECTING.value, Statuses.TC.value]

    @classmethod
    def STATUSES_IDLE(cls) -> list:
        return [
            Statuses.EDITING_QUEUE.value,
            Statuses.CORRECTING_QUEUE.value,
            Statuses.TC_QUEUE.value,
        ]

    @classmethod
    def EDITORS_STATUSES(cls) -> list:
        return [
            Statuses.EDITING_QUEUE.value,
            Statuses.EDITING.value,
            Statuses.CORRECTING_QUEUE.value,
        ]

    @classmethod
    def CORRECTORS_STATUSES(cls) -> list:
        return [
            Statuses.EDITING_QUEUE.value,
            Statuses.EDITING.value,
            Statuses.CORRECTING_QUEUE.value,
            Statuses.CORRECTING.value,
            Statuses.TC_QUEUE.value,
        ]

    @classmethod
    def VERIFIERS_STATUSES(cls) -> list:
        return [
            Statuses.EDITING_QUEUE.value,
            Statuses.CORRECTING_QUEUE.value,
            Statuses.TC_QUEUE.value,
            Statuses.TC.value,
            Statuses.DONE.value,
        ]


class Task(UpdatedModel):
    name = models.CharField(max_length=255, verbose_name="Назва")
    editing_time_estimate = models.PositiveIntegerField(
        default=0, verbose_name="Час на редагування"
    )
    correcting_time_estimate = models.PositiveIntegerField(
        default=0, verbose_name="Час на коректування"
    )
    tc_time_estimate = models.PositiveIntegerField(
        default=0, verbose_name="Час на технічний контроль"
    )
    status = models.CharField(
        max_length=64,
        choices=Statuses.choices,
        default=Statuses.EDITING_QUEUE.value,
        verbose_name="Статус",
    )
    scale = models.IntegerField(
        choices=TaskScales.choices,
        default=TaskScales.FIFTY.value,
        verbose_name="Масштаб",
    )
    category = RangeIntegerField(
        min_value=3, max_value=10, default=3, verbose_name="Категорія складності"
    )
    quarter = models.IntegerField(
        choices=YearQuarter.choices, blank=True, verbose_name="Квартал"
    )
    year = models.PositiveIntegerField(default=date.today().year)
    user = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        related_name="user_tasks",
        verbose_name="Відповідальний користувач",
        blank=True,
        null=True,
    )
    department = models.ForeignKey(
        "Department",
        on_delete=models.PROTECT,
        related_name="department_tasks",
        verbose_name="Відділ",
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated = models.DateTimeField(auto_now=True, verbose_name="Змінено")
    done = models.DateTimeField(blank=True, null=True, verbose_name="Дата завершення")

    def __str__(self):
        return self.name

    @property
    def editing_time_done(self):
        hours_sum = self.task_time_trackers.filter(
            task_status=Statuses.EDITING.value
        ).aggregate(total_hours=Sum("hours"))
        return hours_sum.get("total_hours") or 0

    @property
    def correcting_time_done(self):
        hours_sum = self.task_time_trackers.filter(
            task_status=Statuses.CORRECTING.value
        ).aggregate(total_hours=Sum("hours"))
        return hours_sum.get("total_hours") or 0

    @property
    def tc_time_done(self):
        hours_sum = self.task_time_trackers.filter(
            task_status=Statuses.TC.value
        ).aggregate(total_hours=Sum("hours"))
        return hours_sum.get("total_hours") or 0

    @property
    def involved_users(self):
        return User.objects.filter(user_time_trackers__task_id=self.id).distinct()

    def update_user_in_queue_status(self, status):
        time_trackers = None
        is_queue_status = False

        if status == Statuses.EDITING_QUEUE.value:
            time_trackers = self.task_time_trackers.filter(
                task_status=Statuses.EDITING.value
            )
            is_queue_status = True

        elif status == Statuses.CORRECTING_QUEUE.value:
            time_trackers = self.task_time_trackers.filter(
                task_status=Statuses.CORRECTING.value
            )
            is_queue_status = True

        elif status == Statuses.TC_QUEUE.value:
            time_trackers = self.task_time_trackers.filter(
                task_status=Statuses.TC.value
            )
            is_queue_status = True

        if time_trackers and time_trackers.exists():
            self.user = time_trackers.last().user
            self.save()
            return
        if is_queue_status:
            self.user = None
            self.save()
            return

    def start_time_tracker(self):
        data = {
            "task": self,
            "user": self.user,
            "status": TimeTrackerStatuses.IN_PROGRESS.value,
            "task_status": self.status,
            "task_department": self.department,
        }
        if not TimeTracker.objects.filter(**data).count():
            del data["status"]
            data["start_time"] = datetime.now()
            return TimeTracker.objects.create(**data)

    def create_log_comment(self, log_user, log_text, is_log):
        return Comment.objects.create(
            task=self, user=log_user, body=log_text, is_log=is_log
        )

    @staticmethod
    def check_year_is_correct(year):
        years_before = date.today().year - 3
        years_after = date.today().year + 5
        if year not in range(years_before, years_after + 1):
            raise AssertionError(
                {
                    "year": f"Рік має бути в діапазоні від {years_before} до {years_after}."
                }
            )

    @staticmethod
    def check_name_correspond_to_scale_rule(
        raw_name: str = "", scale: int = 50
    ) -> bool:
        name = raw_name.strip()
        checked_name = regex.match(pattern=TASK_NAME_REGEX.get(scale)[0], string=name)
        errors = []
        if not checked_name:
            raise ValidationError(
                {
                    "name": f"Назва задачі не відповідає правилам написання номенклатури для масштабу {scale} 000"
                }
            )

        for ind, part in enumerate(name.split("-")):
            if part not in TASK_NAME_RULES.get(scale, {}).get(ind, {}).get("rule"):
                errors.append(
                    {ind: TASK_NAME_RULES.get(scale, {}).get(ind, {}).get("error")}
                )
        if errors:
            raise ValidationError(errors)

        return True


class TimeTrackerStatuses(models.TextChoices):
    IN_PROGRESS = "IN_PROGRESS", "В роботі"
    DONE = "DONE", "Завершено"


class TimeTracker(UpdatedModel):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="task_time_trackers",
        verbose_name="Задача",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_time_trackers",
        verbose_name="Виконавець",
        null=True,
        blank=True,
    )
    start_time = models.DateTimeField(verbose_name="Час початку", null=True, blank=True)
    end_time = models.DateTimeField(
        verbose_name="Час закінчення", null=True, blank=True
    )
    hours = models.IntegerField(verbose_name="Час виконання", default=0, blank=True)
    status = models.CharField(
        max_length=64,
        choices=TimeTrackerStatuses.choices,
        default=TimeTrackerStatuses.IN_PROGRESS.value,
        verbose_name="Статус",
    )
    task_status = models.CharField(
        max_length=64,
        choices=Statuses.choices,
        default=Statuses.EDITING_QUEUE.value,
        verbose_name="Статус",
    )
    task_department = models.ForeignKey(
        "Department",
        on_delete=models.PROTECT,
        related_name="department_time_trackers",
        verbose_name="Відділ",
    )

    def __str__(self):
        return f"{self.task.name} - {self.get_status_display()}"

    class Meta:
        ordering = ["start_time"]

    def change_status_done(self):
        self.end_time = datetime.now()
        self.status = TimeTrackerStatuses.DONE
        self.save()

    def _create_tracker(self, data):
        TimeTracker.objects.create(
            task=self.task,
            user=None,
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            status=TimeTrackerStatuses.DONE,
            task_status=Statuses.EDITING_QUEUE.value,
        )

    def handle_update_time(self, changed_time: str, is_start_time: bool):
        date_obj = datetime.fromisoformat(changed_time)

        previous_tracker = TimeTracker.objects.filter(
            id__lt=self.id,
            task__id=self.task.id,
        ).last()
        if not self.end_time:
            next_tracker = None
        else:
            next_tracker = TimeTracker.objects.filter(
                id__gt=self.id,
                task__id=self.task.id,
            ).first()

        if is_start_time and date_obj < self.start_time:
            if not previous_tracker:
                raise ValidationError(
                    {
                        "previous_tracker": "Час старту першого трекера не може бути меншим за час створення його задачі."
                    }
                )
            if previous_tracker and date_obj < previous_tracker.start_time:
                raise ValidationError(
                    {
                        "start_time": "Час старту трекера не може бути ранішим за дату старту попереднього трекера. Спочатку треба видалити попередній трекер."
                    }
                )
            previous_tracker.end_time = date_obj
            previous_tracker.save()
            return

        if is_start_time and date_obj > self.start_time:
            if not previous_tracker:
                raise ValidationError(
                    {
                        "previous_tracker": "Час старту першого трекеру повинен співпадати з часом створення його задачі."
                    }
                )
            if date_obj > datetime.now():
                raise ValidationError(
                    {
                        "start_time": "Час старту трекера не може бути пізнішим ніж поточний час."
                    }
                )

            if self.end_time and date_obj > self.end_time:
                raise ValidationError(
                    {
                        "start_time": "Час старту трекера не може бути пізнішим ніж час закінчення поточного трекера."
                    }
                )

            self._create_tracker(
                data={"start_time": previous_tracker.end_time, "end_time": date_obj}
            )
            return

        if not is_start_time and date_obj > self.end_time:
            if (
                next_tracker
                and next_tracker.end_time
                and date_obj > next_tracker.end_time
            ):
                raise ValidationError(
                    {
                        "end_time": "Час закінчення трекера не може бути пізнішим ніж час закінчення наступного трекера. Спочатку треба видалити наступний трекер."
                    }
                )
            next_tracker.start_time = date_obj
            next_tracker.save()
            return

        if not is_start_time and date_obj < self.end_time and next_tracker:
            if date_obj < self.start_time:
                raise ValidationError(
                    {
                        "end_time": "Час закінчення трекера не може бути раніше його початку"
                    }
                )
            self._create_tracker(
                data={"start_time": date_obj, "end_time": next_tracker.start_time}
            )
            return

    def save(self, *args, **kwargs):
        time_now = self.end_time or datetime.now()
        minute = 60
        half_hour = 30
        if self.start_time:
            diff = business_hours.difference(self.start_time, time_now)
            self.hours = diff.hours
            if (diff.seconds / minute) >= half_hour:
                self.hours += 1
        super(TimeTracker, self).save(*args, **kwargs)


class Comment(UpdatedModel):
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
        ordering = ["-created"]

    def __str__(self):
        return f"{self.user} commented {self.created}"
