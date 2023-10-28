from typing import Type, TypeVar

from damri.django.models.utils import m2m_fields
from django.db.models import Model as Model_
from django.db.models import QuerySet
from simple_history.utils import bulk_create_with_history, bulk_update_with_history

Model = Type[TypeVar("Model", bound=Model_)]


class ModelService:
    MODEL: Model = None
    BULK_UPDATE_EXISTENCE_FIELD = "id"
    BULK_UPDATE_FIELDS: tuple[str, ...] = tuple()

    @classmethod
    def create(cls, obj: Model, *args, **kwargs) -> Model:
        cls.init_obj(obj)
        cls._save(obj)

        return obj

    @classmethod
    def get_or_create(cls, select_related: tuple[str] | None = None, defaults=None, **kwargs) -> tuple[Model, bool]:
        select_related = select_related or tuple()
        return cls.MODEL.objects.select_related(*select_related).get_or_create(**kwargs, defaults=defaults)

    @classmethod
    def update_or_create(cls, defaults=None, **kwargs) -> tuple[Model, bool]:
        return cls.MODEL.objects.update_or_create(**kwargs, defaults=defaults)

    @classmethod
    def init_obj(cls, obj: Model):
        pass

    @classmethod
    def bulk_create_update(
        cls, objs: list[Model] | None = None, create: list | None = None, update: list | None = None
    ):
        if create is None:
            if objs is None:
                raise ValueError("You must provide either create either objs")

            create, update = [], []
            for obj in objs:
                cls._bulk_assign_pk_existing(obj)
                if obj.id:
                    update.append(obj)
                else:
                    create.append(obj)

        if hasattr(cls.MODEL, "history"):
            cls._bulk_create_update_with_history(create, update)
        else:
            cls._bulk_create_update(create, update)

        # bulk m2m
        for m2m_field in m2m_fields(cls.MODEL):
            Through = getattr(cls.MODEL, m2m_field).through
            m2m_objs_create = []

            for obj in [*create, *update]:
                # check if m2m intended
                if not (m2m_objects := getattr(obj, f"_{m2m_field}", None)):
                    continue
                for m2m_object in m2m_objects:
                    m2m_objs_create.append(
                        Through(
                            **{
                                f"{cls.MODEL.__name__.lower()}_id": obj.pk,
                                f"{getattr(cls.MODEL, m2m_field).field.related_model.__name__.lower()}_id": m2m_object.pk,
                            }
                        )
                        # Through(
                        #     **{
                        #         f"{cls.MODEL.__name__.lower()}_id": obj.pk,
                        #         f"{getattr(cls.MODEL, m2m_field).related_model.__name__.lower()}_id": m2m_object.pk,
                        #     }
                        # )
                    )

            # TODO add delete
            # TODO check history
            # Through.objects.delete(delete)
            Through.objects.bulk_create(m2m_objs_create, ignore_conflicts=True)

    @classmethod
    def _save(cls, obj: Model):
        obj.save()

    @classmethod
    def _bulk_create_update_with_history(cls, create: list[Model], update: list[Model]):
        bulk_update_with_history(
            update,
            cls.MODEL,
            fields=cls.BULK_UPDATE_FIELDS,
            batch_size=500,
        )
        bulk_create_with_history(create, cls.MODEL, batch_size=500)

    @classmethod
    def _bulk_create_update(cls, create: list[Model], update: list[Model]):
        # TODO add docstr
        if update:
            if not cls.BULK_UPDATE_FIELDS:
                raise ValueError(f"No specified BULK_UPDATE_FIELDS for {cls.__class__}")
            cls.MODEL.objects.bulk_update(
                update,
                fields=cls.BULK_UPDATE_FIELDS,
                batch_size=500,
            )
        cls.MODEL.objects.bulk_create(create, batch_size=500)

    @classmethod
    def _bulk_assign_pk_existing(cls, obj: Model):
        # TODO add docstr
        existing_ = next(
            (
                potential_existing
                for potential_existing in cls.bulk_iter_potential_existing()
                if getattr(obj, cls.BULK_UPDATE_EXISTENCE_FIELD)
                == getattr(potential_existing, cls.BULK_UPDATE_EXISTENCE_FIELD)
            ),
            None,
        )
        if existing_:
            obj.id = existing_.pk

    @classmethod
    def bulk_iter_potential_existing(cls) -> QuerySet[Model]:
        # TODO add docstr
        return cls.MODEL.objects.all()
