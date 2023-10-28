class ReadOnlyAdminMixin:
    pass
    # can_delete = False

    # def has_add_permission(self, request, obj=None):
    #     return False

    # def has_change_permission(self, request, obj=None):
    #     if "/history/" in request.path and hasattr(obj, "history"):  # for django-simple-history in model history page
    #         return True
    #     return False

    # def has_delete_permission(self, request, obj=None):
    #     return False
