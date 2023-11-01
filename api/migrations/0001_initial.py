# Generated by Django 4.2.1 on 2023-10-30 17:58

import api.fields
import api.validators
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "username",
                    models.CharField(max_length=255, unique=True, verbose_name="Логін"),
                ),
                ("first_name", models.CharField(max_length=255, verbose_name="Ім'я")),
                (
                    "last_name",
                    models.CharField(max_length=255, verbose_name="Прізвище"),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("EDITOR", "Виконавець"),
                            ("CORRECTOR", "Коректувальник"),
                            ("VERIFIER", "Контролер"),
                        ],
                        default="EDITOR",
                        max_length=32,
                        verbose_name="Роль",
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("is_admin", models.BooleanField(default=False)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Department",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=255, unique=True, verbose_name="Відділ"
                    ),
                ),
                (
                    "is_verifier",
                    models.BooleanField(
                        default=False, verbose_name="Перевіряючий відділ"
                    ),
                ),
                (
                    "head",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="deparment_head",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Керівник",
                    ),
                ),
            ],
            options={
                "ordering": ["is_verifier", "id"],
            },
        ),
        migrations.CreateModel(
            name="Status",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=255, unique=True, verbose_name="Статус"
                    ),
                ),
                (
                    "translation",
                    models.CharField(
                        max_length=255, unique=True, verbose_name="Переклад"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="Назва")),
                (
                    "editing_time_estimate",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Час на редагування"
                    ),
                ),
                (
                    "correcting_time_estimate",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Час на коректування"
                    ),
                ),
                (
                    "tc_time_estimate",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Час на технічний контроль"
                    ),
                ),
                (
                    "scale",
                    models.IntegerField(
                        choices=[
                            (25, "1:25 000"),
                            (50, "1:50 000"),
                            (100, "1:100 000"),
                            (200, "1:200 000"),
                            (500, "1:500 000"),
                        ],
                        default=50,
                        verbose_name="Масштаб",
                    ),
                ),
                (
                    "category",
                    api.fields.RangeIntegerField(
                        default=3,
                        validators=[
                            api.validators.KanMinValueValidator(3),
                            api.validators.KanMaxValueValidator(10),
                        ],
                        verbose_name="Категорія складності",
                    ),
                ),
                (
                    "quarter",
                    models.IntegerField(
                        blank=True,
                        choices=[
                            (1, "Перший"),
                            (2, "Другий"),
                            (3, "Третій"),
                            (4, "Четвертий"),
                        ],
                        verbose_name="Квартал",
                    ),
                ),
                ("year", models.PositiveIntegerField(default=2023)),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, verbose_name="Створено"),
                ),
                (
                    "updated",
                    models.DateTimeField(auto_now=True, verbose_name="Змінено"),
                ),
                (
                    "done",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Дата завершення"
                    ),
                ),
                (
                    "department",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="department_tasks",
                        to="api.department",
                        verbose_name="Відділ",
                    ),
                ),
                (
                    "involved_users",
                    models.ManyToManyField(
                        related_name="tasks_involved",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Задіяні користувачі",
                    ),
                ),
                (
                    "status",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="tasks",
                        to="api.status",
                        verbose_name="Статус",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="user_tasks",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Відповідальний користувач",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="TimeTracker",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "start_time",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Час початку"
                    ),
                ),
                (
                    "end_time",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Час закінчення"
                    ),
                ),
                (
                    "hours",
                    models.IntegerField(
                        blank=True, default=0, verbose_name="Час виконання"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("IN_PROGRESS", "В роботі"), ("DONE", "Завершено")],
                        default="IN_PROGRESS",
                        max_length=50,
                        verbose_name="Статус",
                    ),
                ),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="task_time_trackers",
                        to="api.task",
                        verbose_name="Задача",
                    ),
                ),
                (
                    "task_department",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="department_time_trackers",
                        to="api.department",
                        verbose_name="Відділ",
                    ),
                ),
                (
                    "task_status",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="time_trackers",
                        to="api.status",
                        verbose_name="Статус задачі",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_time_trackers",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Виконавець",
                    ),
                ),
            ],
            options={
                "ordering": ["start_time"],
            },
        ),
        migrations.CreateModel(
            name="Comment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("body", models.TextField()),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("is_log", models.BooleanField(default=False)),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="task_comments",
                        to="api.task",
                        verbose_name="Задача",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_comments",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Виконавець",
                    ),
                ),
            ],
            options={
                "ordering": ["-created"],
            },
        ),
        migrations.AddField(
            model_name="user",
            name="department",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="users",
                to="api.department",
                verbose_name="Відділ",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="groups",
            field=models.ManyToManyField(
                blank=True,
                help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                related_name="user_set",
                related_query_name="user",
                to="auth.group",
                verbose_name="groups",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="user_permissions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Specific permissions for this user.",
                related_name="user_set",
                related_query_name="user",
                to="auth.permission",
                verbose_name="user permissions",
            ),
        ),
    ]
