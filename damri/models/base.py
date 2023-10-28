import json
from typing import ClassVar, Hashable

from django.db import models
from pydantic import BaseModel as PydanticBaseModel

null = dict(null=True, blank=True)


# region django


class BaseDjangoModel(models.Model):
    class Meta:
        abstract = True


class TimeStampModel(BaseDjangoModel):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# endregion


# region pydantic


class BaseModel(PydanticBaseModel):
    hash_fields: ClassVar[tuple[str, ...]] = tuple()

    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True

    def jsonable_dict(self) -> dict:
        return json.loads(self.json())

    def values(self) -> list:
        return list(self.dict().values())

    def keys(self) -> list[str]:
        return list(self.dict().keys())

    def __hash__(self):
        values = tuple(
            [
                getattr(self, field)
                for field in (self.hash_fields or self.__dict__.keys())
                if isinstance(field, Hashable)
            ]
        )
        return hash(values)

    @staticmethod
    def unique(objs: list) -> list:
        return list({hash(obj): obj for obj in objs}.values())


class BaseFrozenModel(BaseModel):
    class Config(BaseModel.Config):
        frozen = True


# endregion
