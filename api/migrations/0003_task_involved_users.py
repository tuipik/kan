# Generated by Django 4.2.1 on 2023-10-04 12:04

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0002_alter_timetracker_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="involved_users",
            field=models.ManyToManyField(
                related_name="tasks_involved",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Задіяні користувачі",
            ),
        ),
    ]