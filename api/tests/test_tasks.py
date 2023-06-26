import datetime
import pytest
from rest_framework.reverse import reverse

from api.models import TimeTracker, TaskStatuses, TimeTrackerStatuses
from conftest import create_user_with_department, create_task, default_user_data
from kanban.settings import workday_time, launch_time


@pytest.mark.django_db
def test_CRUD_tasks_ok(api_client, super_user):
    api_client.force_authenticate(super_user)

    department_data = {"name": "test_department"}
    department = api_client.post(reverse("department-list"), data=department_data)
    assert department.data.get("success")

    department_id = department.data.get("data")[0].get("id")
    user = api_client.patch(
        reverse("account-detail", kwargs={"pk": super_user.id}),
        data={"department": department_id},
    )
    assert user.data.get("success")

    task_data = {
        "name": "M-37-103-А",
        "change_time_estimate": 50,
        "correct_time_estimate": 25,
        "otk_time_estimate": 15,
        "quarter": 1,
        "category": "some category",
        "user": user.data.get("data")[0].get("id"),
        "department": department_id,
    }

    # test create
    result = api_client.post(reverse("task-list"), data=task_data)

    assert result.data.get("success")
    assert not result.data.get("errors")
    assert result.data.get("data_len") == 1
    assert result.data.get("message") == "Created"

    all_tasks = api_client.get(reverse("task-list"))

    assert all_tasks.data.get("data_len") == 1
    assert all_tasks.data.get("data")[0].get("name") == task_data.get("name")

    # test put
    task_obj_id = all_tasks.data.get("data")[0].get("id")
    task_data["name"] = "M-36-80-А"

    result = api_client.put(
        reverse("task-detail", kwargs={"pk": task_obj_id}),
        data=task_data,
    )
    assert result.data.get("success")
    assert not result.data.get("errors")
    assert result.data.get("data_len") == 1
    assert result.data.get("message") == "Updated"

    task_updated = api_client.get(reverse("task-detail", kwargs={"pk": task_obj_id}))
    assert task_updated.data.get("data")[0].get("name") == task_data.get("name")

    # test patch
    new_task_name = {"name": "M-35-13-А"}
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task_obj_id}),
        data=new_task_name,
    )
    assert result.data.get("success")
    assert not result.data.get("errors")
    assert result.data.get("data_len") == 1
    assert result.data.get("message") == "Updated"

    task_updated = api_client.get(reverse("task-detail", kwargs={"pk": task_obj_id}))
    assert task_updated.data.get("data")[0].get("name") == new_task_name.get("name")

    # test delete
    result = api_client.delete(reverse("task-detail", kwargs={"pk": task_obj_id}))
    assert result.data.get("success")
    assert not result.data.get("errors")
    assert result.data.get("data_len") == 0
    assert result.data.get("message") == "Deleted"

    all_tasks = api_client.get(reverse("task-list"))
    assert all_tasks.data.get("data_len") == 0


@pytest.mark.django_db
def test_create_time_tracker_on_change_task_in_progress(
    api_client, super_user, freezer
):
    api_client.force_authenticate(super_user)
    user_data = default_user_data(1)
    user, department = create_user_with_department(next(user_data))
    task = create_task(user=user, department=department)
    api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"status": TaskStatuses.IN_PROGRESS},
    )
    # the second run update with status IN_PROGRESS is to test, that only 1 TimeTracker can be IN_PROGRESS at one time
    # and should change status to idle first
    with pytest.raises(Exception) as exc_info:
        api_client.patch(
            reverse("task-detail", kwargs={"pk": task.id}),
            data={"status": TaskStatuses.IN_PROGRESS},
        )
    assert exc_info.type == ValueError

    time_trackers_count = TimeTracker.objects.count()
    time_trackers = TimeTracker.objects.all()
    assert time_trackers_count == 1
    assert time_trackers[0].task.id == task.id
    assert time_trackers[0].user.id == user.id
    assert time_trackers[0].status == TaskStatuses.IN_PROGRESS

    api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"status": TaskStatuses.WAITING},
    )


@pytest.mark.django_db
@pytest.mark.freeze_time('2023-06-05 09:00:00')
def test_change_status_less_4_hours(api_client, super_user, freezer):
    user_data = default_user_data(1)
    user, department = create_user_with_department(next(user_data))
    task = create_task(user=user, department=department)

    api_client.force_authenticate(super_user)

    # task IN_PROGRESS creates time_tracker
    api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"status": TaskStatuses.IN_PROGRESS},
    )

    hours_passed = 3
    freezer.move_to(datetime.datetime.now() + datetime.timedelta(hours=hours_passed))

    # task DONE updates time_tracker with status DONE
    api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"status": TaskStatuses.DONE},
    )
    time_trackers = api_client.get(reverse("time_tracker-list"))

    assert time_trackers.data.get("data")[0].get("status") == TimeTrackerStatuses.DONE
    assert time_trackers.data.get("data")[0].get("hours") == hours_passed
    assert time_trackers.data.get("data")[0].get("end_time")


@pytest.mark.django_db
@pytest.mark.freeze_time('2023-06-05 09:00:00')
def test_change_status_more_4_hours(api_client, super_user, freezer):
    user_data = default_user_data(1)
    user, department = create_user_with_department(next(user_data))
    task = create_task(user=user, department=department)

    api_client.force_authenticate(super_user)

    # task IN_PROGRESS creates time_tracker
    api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"status": TaskStatuses.IN_PROGRESS},
    )

    hours_passed = 5
    freezer.move_to(datetime.datetime.now() + datetime.timedelta(hours=hours_passed))

    # task DONE updates time_tracker with status DONE
    api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"status": TaskStatuses.DONE},
    )
    time_trackers = api_client.get(reverse("time_tracker-list"))

    assert time_trackers.data.get("data")[0].get("status") == TimeTrackerStatuses.DONE
    assert (
        time_trackers.data.get("data")[0].get("hours")
        == hours_passed - launch_time
    )
    assert time_trackers.data.get("data")[0].get("end_time")


@pytest.mark.django_db
@pytest.mark.freeze_time('2023-06-05 09:00:00')
def test_change_status_more_8_hours(api_client, super_user, freezer):
    user_data = default_user_data(1)
    user, department = create_user_with_department(next(user_data))
    task = create_task(user=user, department=department)

    api_client.force_authenticate(super_user)

    # task IN_PROGRESS creates time_tracker
    api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"status": TaskStatuses.IN_PROGRESS},
    )

    hours_passed = 10
    freezer.move_to(datetime.datetime.now() + datetime.timedelta(hours=hours_passed))

    # task DONE updates time_tracker with status DONE
    api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"status": TaskStatuses.DONE},
    )
    time_trackers = api_client.get(reverse("time_tracker-list"))

    assert time_trackers.data.get("data")[0].get("status") == TimeTrackerStatuses.DONE
    assert (
        time_trackers.data.get("data")[0].get("hours")
        == workday_time
    )
    assert time_trackers.data.get("data")[0].get("end_time")
