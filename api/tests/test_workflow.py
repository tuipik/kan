import datetime
import pytest

from rest_framework.reverse import reverse

from api.models import TaskStatuses, TimeTrackerStatuses
from api.utils import update_time_trackers_hours
from conftest import create_user_with_department, create_task, default_user_data
from kanban.settings import launch_time


@pytest.mark.django_db
@pytest.mark.freeze_time("2023-06-05 09:00:00")
def test_workflow_ok(api_client, super_user, freezer):
    """
    Create task -> task waiting -> task in_progress user1 -> task in correct queue without user ->
    -> task in correcting user2 -> task in otk queue without user -> otk user3 -> DONE
    """

    # Create task -> task waiting ->
    user_data = default_user_data(3)
    user_executant, department = create_user_with_department(next(user_data))
    user_corrector, department = create_user_with_department(next(user_data))
    user_otk, department = create_user_with_department(next(user_data))
    task = create_task(department=department)

    # task in_progress user1 ->
    api_client.force_authenticate(super_user)
    task_updated = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"user": user_executant.id, "status": TaskStatuses.IN_PROGRESS},
    )
    time_trackers = api_client.get(
        f'{reverse("time_tracker-list")}?status={TimeTrackerStatuses.IN_PROGRESS}'
    )

    assert task_updated.data.get("data")[0].get("user").get("id") == user_executant.id
    assert task_updated.data.get("data")[0].get("status") == TaskStatuses.IN_PROGRESS
    assert time_trackers.data.get("data_len") == 1
    assert time_trackers.data.get("data")[0].get("task") == task.id
    assert time_trackers.data.get("data")[0].get("user").get("id") == user_executant.id
    assert (
        time_trackers.data.get("data")[0].get("status")
        == TimeTrackerStatuses.IN_PROGRESS
    )

    # task in correct queue without user ->
    hours_passed = 7
    freezer.move_to(datetime.datetime.now() + datetime.timedelta(hours=hours_passed))

    no_user = None
    task_updated = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"user": no_user, "status": TaskStatuses.CORRECTING_QUEUE},
        format="json",
    )
    time_trackers = api_client.get(
        f'{reverse("time_tracker-list")}?task_status={TaskStatuses.IN_PROGRESS}'
    )

    assert task_updated.data.get("data")[0].get("user").get("id") == no_user
    assert (
        task_updated.data.get("data")[0].get("status") == TaskStatuses.CORRECTING_QUEUE
    )
    assert time_trackers.data.get("data_len") == 1
    assert time_trackers.data.get("data")[0].get("task") == task.id
    assert time_trackers.data.get("data")[0].get("user").get("id") == user_executant.id
    assert time_trackers.data.get("data")[0].get("status") == TimeTrackerStatuses.DONE
    assert (
        time_trackers.data.get("data")[0].get("task_status") == TaskStatuses.IN_PROGRESS
    )
    assert time_trackers.data.get("data")[0].get("hours") == hours_passed - launch_time

    # task in correcting user2 ->
    correct_start_time = "2023-06-05 16:00:00"
    freezer.move_to(datetime.datetime.fromisoformat(correct_start_time))
    task_updated = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"user": user_corrector.id, "status": TaskStatuses.CORRECTING},
    )
    time_trackers = api_client.get(
        f'{reverse("time_tracker-list")}?user__id={user_corrector.id}&task_status={TaskStatuses.CORRECTING}'
    )

    assert task_updated.data.get("data")[0].get("user").get("id") == user_corrector.id
    assert task_updated.data.get("data")[0].get("status") == TaskStatuses.CORRECTING
    assert time_trackers.data.get("data_len") == 1
    assert time_trackers.data.get("data")[0].get("task") == task.id
    assert time_trackers.data.get("data")[0].get("user").get("id") == user_corrector.id
    assert (
        time_trackers.data.get("data")[0].get("status")
        == TimeTrackerStatuses.IN_PROGRESS
    )

    # task in otk queue without user ->
    correct_end_time = "2023-06-07 12:00:00"
    correct_working_hours = 13
    freezer.move_to(datetime.datetime.fromisoformat(correct_end_time))

    no_user = None
    task_updated = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"user": no_user, "status": TaskStatuses.OTK_QUEUE},
        format="json",
    )
    time_trackers = api_client.get(
        f'{reverse("time_tracker-list")}?user__id={user_corrector.id}&task_status={TaskStatuses.CORRECTING}'
    )

    assert task_updated.data.get("data")[0].get("user").get("id") == no_user
    assert task_updated.data.get("data")[0].get("status") == TaskStatuses.OTK_QUEUE
    assert time_trackers.data.get("data_len") == 1
    assert time_trackers.data.get("data")[0].get("task") == task.id
    assert time_trackers.data.get("data")[0].get("user").get("id") == user_corrector.id
    assert time_trackers.data.get("data")[0].get("status") == TimeTrackerStatuses.DONE
    assert time_trackers.data.get("data")[0].get("hours") == correct_working_hours

    # task in otk user3 ->
    otk_start_time = "2023-06-08 09:00:00"
    freezer.move_to(datetime.datetime.fromisoformat(otk_start_time))
    task_updated = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"user": user_otk.id, "status": TaskStatuses.OTK},
    )
    time_trackers = api_client.get(
        f'{reverse("time_tracker-list")}?user__id={user_otk.id}&task_status={TaskStatuses.OTK}'
    )

    assert task_updated.data.get("data")[0].get("user").get("id") == user_otk.id
    assert task_updated.data.get("data")[0].get("status") == TaskStatuses.OTK
    assert time_trackers.data.get("data_len") == 1
    assert time_trackers.data.get("data")[0].get("task") == task.id
    assert time_trackers.data.get("data")[0].get("user").get("id") == user_otk.id
    assert (
        time_trackers.data.get("data")[0].get("status")
        == TimeTrackerStatuses.IN_PROGRESS
    )

    # task done without user ->
    otk_end_time = "2023-06-08 13:00:00"
    otk_working_hours = 4
    freezer.move_to(datetime.datetime.fromisoformat(otk_end_time))

    no_user = None
    task_updated = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"user": no_user, "status": TaskStatuses.DONE},
        format="json",
    )
    time_trackers = api_client.get(
        f'{reverse("time_tracker-list")}?user__id={user_otk.id}&task_status={TaskStatuses.OTK}'
    )

    assert task_updated.data.get("data")[0].get("user").get("id") == no_user
    assert task_updated.data.get("data")[0].get("status") == TaskStatuses.DONE
    assert time_trackers.data.get("data_len") == 1
    assert time_trackers.data.get("data")[0].get("task") == task.id
    assert time_trackers.data.get("data")[0].get("user").get("id") == user_otk.id
    assert time_trackers.data.get("data")[0].get("status") == TimeTrackerStatuses.DONE
    assert time_trackers.data.get("data")[0].get("hours") == otk_working_hours


@pytest.mark.django_db
@pytest.mark.freeze_time("2023-06-05 09:00:00")
def test_aggregate_status_time_done(api_client, super_user, freezer):
    user_data = default_user_data(3)
    user_executant_1, department = create_user_with_department(next(user_data))
    user_executant_2, department = create_user_with_department(next(user_data))
    task_1 = create_task(department=department, name="M-36-23-B")
    task_2 = create_task(department=department, name="M-36-101-A")

    api_client.force_authenticate(super_user)
    task_1_updated = api_client.patch(
        reverse("task-detail", kwargs={"pk": task_1.id}),
        data={"user": user_executant_1.id, "status": TaskStatuses.IN_PROGRESS},
    )
    task_2_updated = api_client.patch(
        reverse("task-detail", kwargs={"pk": task_2.id}),
        data={"user": user_executant_2.id, "status": TaskStatuses.IN_PROGRESS},
    )

    hours_passed = 1
    freezer.move_to(datetime.datetime.now() + datetime.timedelta(hours=hours_passed))
    update_time_trackers_hours()
    time_trackers = api_client.get(
        f'{reverse("time_tracker-list")}?status={TimeTrackerStatuses.IN_PROGRESS}'
    )
    assert time_trackers.data.get("data")[0].get("hours") == 1
    assert time_trackers.data.get("data")[1].get("hours") == 1

    hours_passed = 1
    freezer.move_to(datetime.datetime.now() + datetime.timedelta(hours=hours_passed))
    update_time_trackers_hours()
    time_trackers = api_client.get(
        f'{reverse("time_tracker-list")}?status={TimeTrackerStatuses.IN_PROGRESS}'
    )
    assert time_trackers.data.get("data")[0].get("hours") == 2
    assert time_trackers.data.get("data")[1].get("hours") == 2

    hours_passed = 1
    freezer.move_to(datetime.datetime.now() + datetime.timedelta(hours=hours_passed))

    no_user = None
    task_1_updated = api_client.patch(
        reverse("task-detail", kwargs={"pk": task_1.id}),
        data={"user": no_user, "status": TaskStatuses.CORRECTING_QUEUE},
        format="json",
    )

    task_2_updated = api_client.patch(
        reverse("task-detail", kwargs={"pk": task_2.id}),
        data={
            "user": task_2_updated.data.get("data")[0].get("user").get("id"),
            "status": TaskStatuses.STOPPED,
        },
        format="json",
    )

    hours_passed = 1
    freezer.move_to(datetime.datetime.now() + datetime.timedelta(hours=hours_passed))
    task_2_updated = api_client.patch(
        reverse("task-detail", kwargs={"pk": task_2.id}),
        data={
            "user": task_2_updated.data.get("data")[0].get("user").get("id"),
            "status": TaskStatuses.IN_PROGRESS,
        },
        format="json",
    )

    hours_passed = 4
    freezer.move_to(datetime.datetime.now() + datetime.timedelta(hours=hours_passed))
    no_user = None
    task_2_updated = api_client.patch(
        reverse("task-detail", kwargs={"pk": task_2.id}),
        data={"user": no_user, "status": TaskStatuses.CORRECTING_QUEUE},
        format="json",
    )

    assert task_1_updated.data.get("data")[0].get("change_time_done") == 3
    assert task_2_updated.data.get("data")[0].get("change_time_done") == 6
