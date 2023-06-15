# Generated by Django 4.2.1 on 2023-06-09 14:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

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
                ("name", models.CharField(max_length=255, verbose_name="Відділ")),
                (
                    "head",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="head_users",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Керівник",
                    ),
                ),
            ],
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
                    "change_time_estimate",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Час на оновлення"
                    ),
                ),
                (
                    "correct_time_estimate",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Час на корегування"
                    ),
                ),
                (
                    "otk_time_estimate",
                    models.PositiveIntegerField(default=0, verbose_name="Час на ОТК"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("WAITING", "Очікування"),
                            ("IN_PROGRESS", "В роботі"),
                            ("STOPPED", "Призупинено"),
                            ("DONE", "Завершено"),
                            ("CORRECTING", "Корректура"),
                            ("CORRECTING_QUEUE", "Черга корректури"),
                            ("OTK", "ОТК"),
                            ("OTK_QUEUE", "Черга ОТК"),
                        ],
                        default="WAITING",
                        max_length=50,
                        verbose_name="Статус",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, verbose_name="Створено"),
                ),
                (
                    "updated",
                    models.DateTimeField(auto_now=True, verbose_name="Оновлено"),
                ),
                (
                    "done",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Завершено"
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
                (
                    "category",
                    models.CharField(max_length=255, verbose_name="Категорія"),
                ),
                (
                    "department",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="task_departments",
                        to="api.department",
                        verbose_name="Відділ",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="task_users",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Відповідальний",
                    ),
                ),
            ],
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
                    models.DateTimeField(auto_now_add=True, verbose_name="Час початку"),
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
                        choices=[
                            ("IN_PROGRESS", "В роботі"),
                            ("STOPPED", "Призупинено"),
                            ("CANCELED", "Відмінено"),
                            ("DONE", "Завершено"),
                        ],
                        default="IN_PROGRESS",
                        max_length=50,
                        verbose_name="Статус",
                    ),
                ),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="time_tracker_tasks",
                        to="api.task",
                        verbose_name="Задача",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="time_tracker_users",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Виконавець",
                    ),
                ),
            ],
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
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_comments",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Виконавець",
                    ),
                ),
            ],
            options={
                "ordering": ["created"],
            },
        ),
        migrations.AddField(
            model_name="user",
            name="department",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="user_departments",
                to="api.department",
                verbose_name="Відділ",
            ),
        ),
    ]