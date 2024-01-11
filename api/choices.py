from django.db import models


class YearQuarter(models.IntegerChoices):
    FIRST = 1, "Перший"
    SECOND = 2, "Другий"
    THIRD = 3, "Третій"
    FOURTH = 4, "Четвертий"


class TaskScales(models.IntegerChoices):
    TEN = 10, "1:10 000"
    TWENTY_FIVE = 25, "1:25 000"
    FIFTY = 50, "1:50 000"
    ONE_HUNDRED = 100, "1:100 000"
    TWO_HUNDRED = 200, "1:200 000"
    FIVE_HUNDRED = 500, "1:500 000"
    ONE_MILLION = 1000, "1:1 000 000"


class Statuses(models.TextChoices):
    EDITING_QUEUE = "EDITING_QUEUE", "Черга виконання"
    EDITING = "EDITING", "Виконання"
    CORRECTING_QUEUE = "CORRECTING_QUEUE", "Черга коректури"
    CORRECTING = "CORRECTING", "Коректура"
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


class UserRoles(models.TextChoices):
    EDITOR = "EDITOR", "Виконавець"
    CORRECTOR = "CORRECTOR", "Редактор"
    VERIFIER = "VERIFIER", "Технічний контроль"


class TimeTrackerStatuses(models.TextChoices):
    IN_PROGRESS = "IN_PROGRESS", "В роботі"
    DONE = "DONE", "Завершено"
