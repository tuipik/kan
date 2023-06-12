from drf_standardized_errors.formatter import ExceptionFormatter
from drf_standardized_errors.types import ErrorResponse
from rest_framework.utils.serializer_helpers import ReturnList


def make_resp(success=False, accounts=None, msg=None, errors=None):
    if accounts is None:
        accounts = []
    if accounts and type(accounts) not in (list, ReturnList):
        accounts = [accounts]
    if errors:
        errors = f"{errors}"

    return {
        "success": success,
        "accounts": accounts,
        "errors": errors,
        "msg": msg,
    }


class ResponseInfo(object):
    def __init__(self, user=None, **kwargs):
        self.response = {
            "success": kwargs.get("success", True),
            "errors": kwargs.get("errors", None),
            "data_len": 0,
            "data": kwargs.get("data", []),
            "message": kwargs.get("message", None),
        }


class KanExceptionFormatter(ExceptionFormatter):
    def format_error_response(self, error_response: ErrorResponse):
        errors = []
        for error in error_response.errors:
            errors.append(
                {
                    "code": error.code,
                    "detail": error.detail,
                    "attr": error.attr
                }
            )

        resp = ResponseInfo(success=False, errors=errors)
        return resp.response
