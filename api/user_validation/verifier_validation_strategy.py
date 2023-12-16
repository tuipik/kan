from api.models import UserRoles, Statuses

from api.user_validation.base_validation_strategy import BaseValidationStrategy


class VerifierValidationStrategy(BaseValidationStrategy):

    def is_role_and_status(self):
        return (
            self.user.role == UserRoles.VERIFIER.value
            and self.status
            not in [Statuses.TC_QUEUE.value, Statuses.TC.value]
        )
