from typing import Type, TypeVar

from damri.django.webhooks.models import WebHookEvent
from damri.services.models import ModelService

EventModel = Type[TypeVar("EventModel", bound=WebHookEvent)]


class WebHookEventModelService(ModelService):
    MODEL: EventModel

    @classmethod
    def save_webhook(cls, request):
        obj = cls.MODEL(data_received=request.data)
        cls.create(obj)
