import django_filters

from api.models import User, Task, TimeTracker, Comment, Department


class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = {
            "username": ["exact", "in", "contains", "icontains"],
            "first_name": ["exact", "in", "contains", "icontains"],
            "last_name": ["exact", "in", "contains", "icontains"],
            "department__id": ["exact", "in"],
            "department__name": ["exact", "in", "contains", "icontains"],
            "is_active": ["exact"],
            "role": ["exact", "in"],
            "is_admin": ["exact"],
        }


class DepartmentFilter(django_filters.FilterSet):
    class Meta:
        model = Department
        fields = {
            "name": ["exact", "in", "contains", "icontains"],
            "head__id": ["exact", "in", "contains", "icontains"],
            "head__username": ["exact", "in", "contains", "icontains"],
            "head__role": ["exact", "in"],
            "is_verifier": ["exact"],
        }


class TaskFilter(django_filters.FilterSet):
    class Meta:
        model = Task
        fields = {
            "id": ["exact", "in", "contains", "icontains"],
            "name": ["exact", "in", "contains", "icontains"],
            "status": ["exact", "in"],
            "scale": ["exact", "in"],
            "department__id": ["exact", "in"],
            "department__name": ["exact", "contains", "icontains"],
            "user__id": ["exact", "in"],
            "user__username": ["exact", "contains", "icontains"],
            "user__first_name": ["exact", "contains", "icontains"],
            "user__last_name": ["exact", "contains", "icontains"],
            "user__role": ["exact", "in", "contains", "icontains"],
            "quarter": ["exact", "in"],
            "year": ["exact", "gt", "gte", "lt", "lte", "in"],
            "editing_time_estimate": ["exact", "gt", "gte", "lt", "lte"],
            "correcting_time_estimate": ["exact", "gt", "gte", "lt", "lte"],
            "tc_time_estimate": ["exact", "gt", "gte", "lt", "lte"],
            "category": ["exact", "gt", "gte", "lt", "lte"],
            "created": ["exact", "gt", "gte", "lt", "lte"],
            "updated": ["exact", "gt", "gte", "lt", "lte"],
            "done": ["exact", "gt", "gte", "lt", "lte"],
        }


class TimeTrackerFilter(django_filters.FilterSet):
    class Meta:
        model = TimeTracker
        fields = {
            "id": ["exact", "in", "gt", "gte", "lt", "lte"],
            "task__id": ["exact", "in"],
            "task__name": ["exact", "in", "contains", "icontains"],
            "user__id": ["exact"],
            "user__username": ["exact", "contains", "icontains"],
            "user__first_name": ["exact", "contains", "icontains"],
            "user__last_name": ["exact", "contains", "icontains"],
            "user__role": ["exact", "in", "contains", "icontains"],
            "start_time": ["exact", "gt", "gte", "lt", "lte"],
            "end_time": ["exact", "gt", "gte", "lt", "lte"],
            "hours": ["exact", "gt", "gte", "lt", "lte"],
            "status": ["exact"],
            "task_status": ["exact", "in"],
            "task_department": ["exact", "in"],
        }


class CommentFilter(django_filters.FilterSet):
    class Meta:
        model = Comment
        fields = {
            "task__id": ["exact", "in"],
            "task__name": ["exact", "in", "contains", "icontains"],
            "user__id": ["exact", "in"],
            "user__username": ["exact", "contains", "icontains"],
            "user__first_name": ["exact", "contains", "icontains"],
            "user__last_name": ["exact", "contains", "icontains"],
            "body": ["exact", "contains", "icontains"],
            "created": ["exact", "gt", "gte", "lt", "lte"],
        }
