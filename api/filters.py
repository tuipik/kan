import django_filters

from api.models import User, Task, TimeTracker, Comment, Department


class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = {
            "username": ["exact", "contains", "icontains"],
            "first_name": ["exact", "contains", "icontains"],
            "last_name": ["exact", "contains", "icontains"],
            "department__id": ["exact"],
            "department__name": ["exact", "contains", "icontains"],
            "department__statuses__id": ["exact", "contains", "icontains"],
            "is_active": ["exact"],
        }


class DepartmentFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Department
        fields = ["name"]


class TaskFilter(django_filters.FilterSet):
    class Meta:
        model = Task
        fields = {
            "name": ["exact", "contains", "icontains"],
            "status": ["exact"],
            "scale": ["exact"],
            "department__id": ["exact"],
            "department__name": ["exact", "contains", "icontains"],
            "primary_department__id": ["exact"],
            "primary_department__name": ["exact", "contains", "icontains"],
            "user__id": ["exact"],
            "user__username": ["exact", "contains", "icontains"],
            "user__first_name": ["exact", "contains", "icontains"],
            "user__last_name": ["exact", "contains", "icontains"],
            "quarter": ["exact", "in"],
            "year": ["exact", "gt", "gte", "lt", "lte"],
            "change_time_estimate": ["exact", "gt", "gte", "lt", "lte"],
            "correct_time_estimate": ["exact", "gt", "gte", "lt", "lte"],
            "vtk_time_estimate": ["exact", "gt", "gte", "lt", "lte"],
            "category": ["exact", "gt", "gte", "lt", "lte"],
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
            "start_time": ["exact", "gt", "gte", "lt", "lte"],
            "end_time": ["exact", "gt", "gte", "lt", "lte"],
            "hours": ["exact", "gt", "gte", "lt", "lte"],
            "status": ["exact"],
            "task_status": ["exact"],
        }


class CommentFilter(django_filters.FilterSet):
    class Meta:
        model = Comment
        fields = {
            "task__id": ["exact", "in"],
            "task__name": ["exact", "in", "contains", "icontains"],
            "user__id": ["exact"],
            "user__username": ["exact", "contains", "icontains"],
            "user__first_name": ["exact", "contains", "icontains"],
            "user__last_name": ["exact", "contains", "icontains"],
            "body": ["exact", "contains", "icontains"],
            "created": ["exact", "gt", "gte", "lt", "lte"],
        }
