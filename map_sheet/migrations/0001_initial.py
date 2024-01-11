# Generated by Django 4.2.1 on 2024-01-10 12:43

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MapSheet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scale', models.IntegerField(choices=[(10, '1:10 000'), (25, '1:25 000'), (50, '1:50 000'), (100, '1:100 000'), (200, '1:200 000'), (500, '1:500 000'), (1000, '1:1 000 000')], default=50, verbose_name='Масштаб')),
                ('name', models.CharField(max_length=15, verbose_name='Назва')),
                ('row', models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F', 'F'), ('G', 'G'), ('H', 'H'), ('I', 'I'), ('J', 'J'), ('K', 'K'), ('L', 'L'), ('M', 'M'), ('N', 'N'), ('O', 'O'), ('P', 'P'), ('Q', 'Q'), ('R', 'R'), ('S', 'S'), ('T', 'T'), ('U', 'U'), ('V', 'V')], max_length=1, verbose_name='Ряд')),
                ('column', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(60)], verbose_name='Колона')),
                ('square_500k', models.CharField(choices=[('А', 'А'), ('Б', 'Б'), ('В', 'В'), ('Г', 'Г')], max_length=1, null=True, verbose_name='Квадрат 500 000')),
                ('square_200k', models.CharField(choices=[('I', 'I'), ('II', 'II'), ('III', 'III'), ('IV', 'IV'), ('V', 'V'), ('VI', 'VI'), ('VII', 'VII'), ('VIII', 'VIII'), ('IX', 'IX'), ('X', 'X'), ('XI', 'XI'), ('XII', 'XII'), ('XIII', 'XIII'), ('XIV', 'XIV'), ('XV', 'XV'), ('XVI', 'XVI'), ('XVII', 'XVII'), ('XVIII', 'XVIII'), ('XIX', 'XIX'), ('XX', 'XX'), ('XXI', 'XXI'), ('XXII', 'XXII'), ('XXIII', 'XXIII'), ('XXIV', 'XXIV'), ('XXV', 'XXV'), ('XXVI', 'XXVI'), ('XXVII', 'XXVII'), ('XXVIII', 'XXVIII'), ('XXIX', 'XXIX'), ('XXX', 'XXX'), ('XXXI', 'XXXI'), ('XXXII', 'XXXII'), ('XXXIII', 'XXXIII'), ('XXXIV', 'XXXIV'), ('XXXV', 'XXXV'), ('XXXVI', 'XXXVI')], max_length=6, null=True, verbose_name='Квадрат 200 000')),
                ('square_100k', models.PositiveSmallIntegerField(null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(144)], verbose_name='Квадрат 100 000')),
                ('square_50k', models.CharField(choices=[('А', 'А'), ('Б', 'Б'), ('В', 'В'), ('Г', 'Г')], max_length=1, null=True, verbose_name='Квадрат 50 000')),
                ('square_25k', models.CharField(choices=[('а', 'а'), ('б', 'б'), ('в', 'в'), ('г', 'г')], max_length=1, null=True, verbose_name='Квадрат 25 000')),
                ('square_10k', models.PositiveSmallIntegerField(null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4)], verbose_name='Квадрат 10 000')),
                ('year', models.PositiveIntegerField(default=2024, verbose_name='Рік')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Створено')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Змінено')),
            ],
        ),
    ]
