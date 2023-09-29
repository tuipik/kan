# Generated by Django 4.2.1 on 2023-09-29 11:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="timetracker",
            options={"ordering": ["start_time"]},
        ),
        migrations.AlterField(
            model_name="timetracker",
            name="start_time",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Час початку"
            ),
        ),
    ]
