from datetime import date

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from api.CONSTANTS import TRAPEZE_500K_AND_50K_CHOICES, COLUMN_MAX, ROMAN_NUMBERS, ROWS_CHOICES, \
    TRAPEZE_25K_CHOICES, TRAPEZE_100K_MAX, TRAPEZE_10K_MAX
from api.models import TaskScales


class MapSheet(models.Model):
    scale = models.IntegerField(
        choices=TaskScales.choices,
        default=TaskScales.FIFTY.value,
        verbose_name="Масштаб",
    )

    name = models.CharField(max_length=15, verbose_name="Назва")

    row = models.CharField(max_length=1, choices=((i, i) for i in ROWS_CHOICES), verbose_name="Ряд")
    column = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(COLUMN_MAX)], verbose_name="Колона"
    )
    square_500k = models.CharField(
        choices=((i, i) for i in TRAPEZE_500K_AND_50K_CHOICES), null=True, max_length=1, verbose_name="Квадрат 500 000"
    )
    square_200k = models.CharField(
        choices=((i, i) for i in ROMAN_NUMBERS), null=True, max_length=6, verbose_name="Квадрат 200 000"
    )
    square_100k = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(TRAPEZE_100K_MAX)], null=True, verbose_name="Квадрат 100 000"
    )
    square_50k = models.CharField(
        choices=((i, i) for i in TRAPEZE_500K_AND_50K_CHOICES), null=True, max_length=1, verbose_name="Квадрат 50 000"
    )
    square_25k = models.CharField(
        choices=((i, i) for i in TRAPEZE_25K_CHOICES), null=True, max_length=1, verbose_name="Квадрат 25 000"
    )
    square_10k = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(TRAPEZE_10K_MAX)], null=True, verbose_name="Квадрат 10 000"
    )

    year = models.PositiveIntegerField(default=date.today().year, verbose_name="Рік")

    created = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated = models.DateTimeField(auto_now=True, verbose_name="Змінено")

    def __str__(self):
        return f'<MapSheet {self.name=} {self.year=}>'
