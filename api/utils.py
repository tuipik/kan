from drf_standardized_errors.formatter import ExceptionFormatter
from drf_standardized_errors.types import ErrorResponse

from api.models import TaskStatuses, TimeTracker, TimeTrackerStatuses

TASK_STATUSES_PROGRESS = [
    TaskStatuses.IN_PROGRESS,
    TaskStatuses.CORRECTING,
    TaskStatuses.OTK,
]

TASK_STATUSES_IDLE = [
    TaskStatuses.WAITING,
    TaskStatuses.CORRECTING_QUEUE,
    TaskStatuses.OTK_QUEUE,
    TaskStatuses.STOPPED,
    TaskStatuses.DONE,
]


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
        for tracker in time_trackers:
            tracker.update_progress_hours()
