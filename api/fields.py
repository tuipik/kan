from django.db import models

from api.validators import KanMinValueValidator, KanMaxValueValidator


class RangeIntegerField(models.IntegerField):
    def __init__(self, *args, **kwargs):
        validators = kwargs.pop("validators", [])

        min_value = kwargs.pop("min_value", None)
        if min_value is not None:
            validators.append(KanMinValueValidator(min_value))

        max_value = kwargs.pop("max_value", None)
        if max_value is not None:
            validators.append(KanMaxValueValidator(max_value))

        kwargs["validators"] = validators

        super().__init__(*args, **kwargs)
