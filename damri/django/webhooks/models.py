from django.db import models
from django.utils.translation import gettext as _

from damri.models.base import BaseModel
from damri.utils.datetime import now


def default_json():
    return {}


class WebHookEvent(BaseModel):
    created = models.DateTimeField(default=now, verbose_name=_("Время cоздания"))
    updated = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    data_received = models.JSONField(verbose_name=_("Полученныe Данные"), default=default_json)

    class Meta:
        abstract = True
