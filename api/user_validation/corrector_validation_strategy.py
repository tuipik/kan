from api.models import UserRoles, Statuses

from api.user_validation.base_validation_strategy import BaseValidationStrategy


class CorrectorValidationStrategy(BaseValidationStrategy):

    def is_role_and_status(self):
        return (
            self.user.role == UserRoles.CORRECTOR.value
            and self.status
            not in [Statuses.EDITING_QUEUE.value, Statuses.CORRECTING_QUEUE.value, Statuses.CORRECTING.value]
        )
