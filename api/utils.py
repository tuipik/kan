from drf_standardized_errors.formatter import ExceptionFormatter
from drf_standardized_errors.types import ErrorResponse

from api.models import TimeTracker
from api.choices import TimeTrackerStatuses


class ResponseInfo(object):
    def __init__(self, user=None, **kwargs):
        self.response = {
            "success": kwargs.get("success", True),
            "errors": kwargs.get("errors", None),
            "data_len": len(kwargs.get("data", [])),
            "data": kwargs.get("data", []),
            "message": kwargs.get("message", None),
        }


class KanExceptionFormatter(ExceptionFormatter):
    def format_error_response(self, error_response: ErrorResponse):
        errors = []
        for error in error_response.errors:
            errors.append(
                {"code": error.code, "detail": error.detail, "attr": error.attr}
            )

        resp = ResponseInfo(success=False, errors=errors)
        return resp.response


def update_time_trackers_hours():
    """
    Start in cron once an hour to update time-trackers hours
    """
    time_trackers = TimeTracker.objects.filter(status=TimeTrackerStatuses.IN_PROGRESS)
    if time_trackers:
        task_ids = []
        for tracker in time_trackers:
            tracker.save()
            task_ids.append(tracker.task.id)
        return f'Updated time for {len(time_trackers)} tasks. Task ids: {task_ids}'
