from typing import TypeVar

from django.db import models

Model = TypeVar("Model", bound=models.Model)


def m2m_fields(model: Model) -> set[str]:
    m2m_names = set()
    for m2m in model._meta.many_to_many:
        m2m_names.add(m2m.attname)

    return m2m_names
