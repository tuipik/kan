from rest_framework import permissions


class PermissionPolicyMixin:
    def check_permissions(self, request):
        try:
            handler = getattr(self, request.method.lower())
        except AttributeError:
            handler = None

        if (
            handler
            and self.permission_classes_per_method
            and self.permission_classes_per_method.get(handler.__name__)
        ):
            self.permission_classes = self.permission_classes_per_method.get(
                handler.__name__
            )

        super().check_permissions(request)


class OwnerOrAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if obj.user == request.user or request.user.is_admin:
            return True
        return False


class TimeTrackerChangeIsAdminOrIsDepartmentHead(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.task.department.head == request.user or request.user.is_admin
