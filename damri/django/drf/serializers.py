from django.core.exceptions import ObjectDoesNotExist
from rest_framework.serializers import (
    ModelSerializer,
    PrimaryKeyRelatedField,
    Serializer,
)


class ModelRelatedField(PrimaryKeyRelatedField):
    """
    Расширенное поле с возможностью менять название `pk`-поля
    """

    def __init__(self, pk_field_name: str = "pk", first=False, **kwargs):
        super().__init__(**kwargs)
        self.pk_field_name = pk_field_name
        self.first = first

    def to_internal_value(self, data):
        if self.pk_field is not None:
            data = self.pk_field.to_internal_value(data)
        queryset = self.get_queryset()
        try:
            if isinstance(data, bool):
                raise TypeError
            if self.first:
                return queryset.filter(**{self.pk_field_name: data}).first()
            return queryset.get(**{self.pk_field_name: data})
        except ObjectDoesNotExist:
            self.fail("does_not_exist", pk_value=data)
        except (TypeError, ValueError):
            self.fail("incorrect_type", data_type=type(data).__name__)


class ReadOnlyMixin:
    def create(self, *args, **kwargs):
        raise NotImplementedError

    def update(self, *args, **kwargs):
        raise NotImplementedError


class BaseSerializer(Serializer):
    pass


class BaseModelSerializer(ModelSerializer):
    pass
