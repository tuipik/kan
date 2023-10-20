from django.core.validators import BaseValidator


class KanMaxValueValidator(BaseValidator):
    message = "Переконайтеся, що значення менше або дорівнює %(limit_value)s."
    code = "max_value"

    def compare(self, a, b):
        return a > b


class KanMinValueValidator(BaseValidator):
    message = "Переконайтеся, що значення більше або дорівнює %(limit_value)s."
    code = "min_value"

    def compare(self, a, b):
        return a < b

