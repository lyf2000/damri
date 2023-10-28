from typing import Type, TypeVar

from damri.django.webhooks.services.models.webhook_event import WebHookEventModelService
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

EventService = Type[TypeVar("EventService", bound=WebHookEventModelService)]


class WebhookRequestHandlerAPIView(APIView):
    EVENT_SERVICE: EventService = None

    def post(self, request, format=None):
        self._save_webhook_event()
        return Response(status=HTTP_200_OK)

    def _save_webhook_event(self):
        self.EVENT_SERVICE.save_webhook(self.request)
