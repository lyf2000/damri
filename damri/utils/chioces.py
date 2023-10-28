from django.db.models import IntegerChoices as DjangoIntegerChoices
from django.db.models import TextChoices as DjangoTextChoices


class BaseChoices:
    @classmethod
    def as_dict(cls, reversed=False) -> dict:
        return dict(cls.choices) if not reversed else (dict([(value, key) for key, value in cls.choices]))

    @classmethod
    def keys(cls):
        return list(cls.as_dict().keys())


class TextChoices(BaseChoices, DjangoTextChoices):
    pass


class IntegerChoices(BaseChoices, DjangoIntegerChoices):
    pass
