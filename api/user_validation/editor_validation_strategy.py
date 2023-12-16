# from api.models import UserRoles, Statuses
# from rest_framework.exceptions import ValidationError
#
# from api.user_validation.base_validation_strategy import BaseValidationStrategy
#
#
# class EditorValidationStrategy(BaseValidationStrategy):
#
#     def validate(self):
#         return (
#             self.department
#             and self.task
#             and self.department.id != self.task.department_id
#             and (
#                 not self.request_user.is_admin
#                 or self.request_user.id
#                 != self.task.department.head.id
#             )
#         )
#             # raise ValidationError(
#             #     {
#             #         "department": "Відділ може змінити тільки адміністратор або керівник відділу для якого створено задачу"
#             #     }
#             # )
#         if self.user and self.department:
#             if self.user.department_id != self.department.id:
#                 raise ValidationError(
#                     {
#                         "department": "Виконавцем можна призначити тільки користувача з відділу для якого створено задачу"
#                     }
#                 )
#         if self.user and self.task and not self.department and not self.request_user.is_admin and self.status != Statuses.DONE.value:
#
#             if self.user.department_id != self.task.department_id and (
#                 self.user.role not in [UserRoles.CORRECTOR.value, UserRoles.VERIFIER.value]
#                 or (
#                     self.user.role == UserRoles.CORRECTOR.value
#                     and self.status
#                     not in [Statuses.EDITING_QUEUE.value, Statuses.CORRECTING_QUEUE.value, Statuses.CORRECTING.value]
#                 )
#                 or (
#                     self.user.role == UserRoles.VERIFIER.value
#                     and self.status
#                     not in [Statuses.TC_QUEUE.value, Statuses.TC.value]
#                 )
#             ):
#                 raise ValidationError(
#                     {
#                         "department": "Виконавцем можна призначити тільки користувача з відділу для якого створено задачу"
#                     }
#                 )
# #def _is_validated_data_with_user(self):
# #    return "user" in self.validated_data
#
#         if (
#             not self.user
#            # and not self._is_validated_data_with_user()
#             and "user" not in self.validated_data
#             and self.task
#             and self.department
#         ):
#             if self.task.user:
#                 if self.task.user.department_id != self.department.id:
#                     raise ValidationError(
#                         {
#                             "user": "Не можна змінити відділ і залишити відповідальним користувача з іншого відділу"
#                         }
#                     )
