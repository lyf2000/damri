from rest_framework.viewsets import GenericViewSet


class BaseGenericViewSet(GenericViewSet):
    action_serializer_class = {}
    action_permissions = {}
    action_queryset = {}

    def get_serializer_class(self):
        return self.action_serializer_class.get(self.action) or super().get_serializer_class()

    def get_permissions(self):
        return (
            super().get_permissions()
            if (custom_permissions := self.action_permissions.get(self.action)) is None
            else custom_permissions
        )

    def get_queryset(self):
        return self.action_queryset.get(self.action) or super().get_queryset()
