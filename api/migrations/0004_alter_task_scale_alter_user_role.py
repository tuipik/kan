# Generated by Django 4.2.1 on 2024-01-09 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_task_status_alter_task_year_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='scale',
            field=models.IntegerField(choices=[(10, '1:10 000'), (25, '1:25 000'), (50, '1:50 000'), (100, '1:100 000'), (200, '1:200 000'), (500, '1:500 000'), (1000, '1:1 000 000')], default=50, verbose_name='Масштаб'),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('EDITOR', 'Виконавець'), ('CORRECTOR', 'Редактор'), ('VERIFIER', 'Технічний контроль')], default='EDITOR', max_length=32, verbose_name='Роль'),
        ),
    ]