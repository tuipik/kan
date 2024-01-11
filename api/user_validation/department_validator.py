from api.models import Statuses
from api.choices import UserRoles


class DepartmentValidator:

    def __init__(self, validated_data, task, request_user, status):
        self.validated_data = validated_data
        self.task = task
        self.request_user = request_user
        self.status = status
        self.department = validated_data.get("department", None)
        self.user = validated_data.get("user") or (
            task.user if task else None
        )

    def validate_verifier_status(self):
        return (
            self.user.role == UserRoles.VERIFIER.value
            and self.status
            not in [Statuses.TC_QUEUE.value, Statuses.TC.value]
        )

    def validate_corrector_status(self):
        return (
            self.user.role == UserRoles.CORRECTOR.value
            and self.status
            not in [Statuses.EDITING_QUEUE.value, Statuses.CORRECTING_QUEUE.value, Statuses.CORRECTING.value]
        )

    def not_admin_or_not_head(self):
        return (
            not self.request_user.is_admin
            or self.request_user.id != self.task.department.head.id
        )

    def is_vd_department_and_task_department_different(self):
        vd_department = self.validated_data.get("department", None)
        return (
            vd_department
            and self.task
            and vd_department.id != self.task.department_id
        )

