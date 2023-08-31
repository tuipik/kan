from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task
def update_task_time_in_progress():
    from api.utils import update_time_trackers_hours

    result = update_time_trackers_hours()
    logger.info(result)
