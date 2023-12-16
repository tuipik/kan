from api.models import UserRoles, Statuses

from api.user_validation.base_validation_strategy import BaseValidationStrategy


class AdminValidationStrategy(BaseValidationStrategy):

    def not_admin_not_head(self):
        return (
            not self.request_user.is_admin
            or self.request_user.id != self.task.department.head.id
        )
