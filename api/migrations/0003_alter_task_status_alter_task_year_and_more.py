# Generated by Django 4.2.1 on 2024-01-05 14:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0002_alter_user_role"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="status",
            field=models.CharField(
                choices=[
                    ("EDITING_QUEUE", "Черга виконання"),
                    ("EDITING", "Виконання"),
                    ("CORRECTING_QUEUE", "Черга коректури"),
                    ("CORRECTING", "Коректура"),
                    ("TC_QUEUE", "Черга технічного контролю"),
                    ("TC", "Технічний контроль"),
                    ("DONE", "Завершено"),
                ],
                default="EDITING_QUEUE",
                max_length=64,
                verbose_name="Статус",
            ),
        ),
        migrations.AlterField(
            model_name="task",
            name="year",
            field=models.PositiveIntegerField(default=2024),
        ),
        migrations.AlterField(
            model_name="timetracker",
            name="task_status",
            field=models.CharField(
                choices=[
                    ("EDITING_QUEUE", "Черга виконання"),
                    ("EDITING", "Виконання"),
                    ("CORRECTING_QUEUE", "Черга коректури"),
                    ("CORRECTING", "Коректура"),
                    ("TC_QUEUE", "Черга технічного контролю"),
                    ("TC", "Технічний контроль"),
                    ("DONE", "Завершено"),
                ],
                default="EDITING_QUEUE",
                max_length=64,
                verbose_name="Статус",
            ),
        ),
    ]
