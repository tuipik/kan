import datetime

import pytest
from rest_framework.reverse import reverse

from api.models import TimeTrackerStatuses, TimeTracker, BaseStatuses, Status
from api.utils import fill_up_statuses


@pytest.mark.django_db
@pytest.mark.freeze_time("2023-06-05 09:00:00")
def test_CRUD_time_tracker_ok(api_client, super_user, freezer):
    fill_up_statuses()

    api_client.force_authenticate(super_user)

    statuses = Status.objects.filter(name__in=[BaseStatuses.WAITING.name, BaseStatuses.IN_PROGRESS.name])
    department_data = {"name": "test_department", "statuses": [statuses[0].id, statuses[1].id]}
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
        "scale": "50",
        "change_time_estimate": 50,
        "correct_time_estimate": 25,
        "otk_time_estimate": 15,
        "quarter": 1,
        "category": 3,
        "user": user.data.get("data")[0].get("id"),
        "department": department_id,
        "primary_department": department_id,
    }

    task = api_client.post(reverse("task-list"), data=task_data, format='json')
    assert task.data.get("success")
    task_id = task.data.get("data")[0].get("id")

    TimeTracker.objects.all().delete()  # Delete all TimeTracker objects, cause one with status Waiting creates on creating Task

    # test create
    time_tracker_data = {
        "task": task_id,
        "user": user.data.get("data")[0].get("id"),
        'task_status': task.data['data'][0]['status'],
        "start_time": datetime.datetime.now(),
    }

    result = api_client.post(reverse("time_tracker-list"), data=time_tracker_data)

    assert result.data.get("success")
    assert not result.data.get("errors")
    assert result.data.get("data_len") == 1
    assert result.data.get("message") == "Created"

    all_time_trackers = api_client.get(f'{reverse("time_tracker-list")}?status={TimeTrackerStatuses.IN_PROGRESS.name}')

    assert all_time_trackers.data.get("data_len") == 1
    assert all_time_trackers.data.get("data")[0].get("task") == time_tracker_data.get(
        "task"
    )
    assert all_time_trackers.data.get("data")[0].get("user") == time_tracker_data.get("user")
    assert not all_time_trackers.data.get("data")[0].get("end_time")
    assert all_time_trackers.data.get("data")[0].get("hours") == 0
    assert (
        all_time_trackers.data.get("data")[0].get("status")
        == TimeTrackerStatuses.IN_PROGRESS
    )

    # test put
    hours_passed = 1
    freezer.move_to(
        datetime.datetime.now() + datetime.timedelta(hours=hours_passed, minutes=20)
    )

    time_tracker_obj_id = all_time_trackers.data.get("data")[0].get("id")
    time_tracker_data["status"] = TimeTrackerStatuses.DONE

    result = api_client.put(
        reverse("time_tracker-detail", kwargs={"pk": time_tracker_obj_id}),
        data=time_tracker_data,
    )
    assert result.data.get("success")
    assert not result.data.get("errors")
    assert result.data.get("data_len") == 1
    assert result.data["data"][0].get("hours") == hours_passed
    assert result.data.get("message") == "Updated"

    time_tracker_updated = api_client.get(
        reverse("time_tracker-detail", kwargs={"pk": time_tracker_obj_id})
    )
    assert time_tracker_updated.data.get("data")[0].get(
        "status"
    ) == time_tracker_data.get("status")

    # test patch
    TimeTracker.objects.filter(pk=time_tracker_obj_id).update(
        status=TimeTrackerStatuses.IN_PROGRESS
    )
    new_time_tracker_status = {"status": TimeTrackerStatuses.DONE}
    result = api_client.patch(
        reverse("time_tracker-detail", kwargs={"pk": time_tracker_obj_id}),
        data=new_time_tracker_status,
    )
    assert result.data.get("success")
    assert not result.data.get("errors")
    assert result.data.get("data_len") == 1
    assert result.data.get("message") == "Updated"

    time_tracker_updated = api_client.get(
        reverse("time_tracker-detail", kwargs={"pk": time_tracker_obj_id})
    )
    assert time_tracker_updated.data.get("data")[0].get(
        "status"
    ) == new_time_tracker_status.get("status")

    # test delete
    result = api_client.delete(
        reverse("time_tracker-detail", kwargs={"pk": time_tracker_obj_id})
    )
    assert result.data.get("success")
    assert not result.data.get("errors")
    assert result.data.get("data_len") == 0
    assert result.data.get("message") == "Deleted"

    all_time_trackers = api_client.get(reverse("time_tracker-list"))
    assert all_time_trackers.data.get("data_len") == 0


@pytest.mark.django_db
@pytest.mark.freeze_time("2023-06-05 10:00:00")
def test_update_start_time_lt_fake_time(api_client, super_user, freezer):
    fill_up_statuses()

    api_client.force_authenticate(super_user)

    statuses = Status.objects.filter(name__in=[BaseStatuses.WAITING.name, BaseStatuses.IN_PROGRESS.name])
    department_data = {"name": "test_department", "statuses": [statuses[0].id, statuses[1].id]}
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
        "scale": "50",
        "change_time_estimate": 50,
        "correct_time_estimate": 25,
        "otk_time_estimate": 15,
        "quarter": 1,
        "category": "some category",
        "user": user.data.get("data")[0].get("id"),
        "department": department_id,
        "primary_department": department_id,
    }

    task = api_client.post(reverse("task-list"), data=task_data, format='json')

    assert task.data.get("success")

    time_tracker = TimeTracker.objects.filter(status=TimeTrackerStatuses.IN_PROGRESS).first()
    time_tracker_new_start_time = {"start_time": time_tracker.start_time - datetime.timedelta(minutes=30)}
    result = api_client.patch(
        reverse("time_tracker-detail", kwargs={"pk": time_tracker.id}),
        data=time_tracker_new_start_time,
    )

    assert not result.data.get("success")
    assert result.data.get("errors")[0].get("attr") == "previous_tracker"

    # change Fake Time to 12:00
    hours_passed = 2
    freezer.move_to(datetime.datetime.now() + datetime.timedelta(hours=hours_passed))

    # update task status to IN_PROGRESS
    all_tasks = api_client.get(reverse("task-list"))
    task_obj_id = all_tasks.data.get("data")[0].get("id")
    status_progress = Status.objects.get_or_none(name=BaseStatuses.IN_PROGRESS.name)
    new_task_status = {"status": status_progress.id}
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task_obj_id}),
        data=new_task_status,
        format="json",
    )

    assert result.data.get("success")

    # Change start time for second tracker to 9:40
    second_time_tracker = TimeTracker.objects.get_or_none(status=TimeTrackerStatuses.IN_PROGRESS)
    second_time_trackers_new_start_time = {"start_time": second_time_tracker.start_time - datetime.timedelta(hours=2, minutes=20)}
    result = api_client.patch(
        reverse("time_tracker-detail", kwargs={"pk": second_time_tracker.id}),
        data=second_time_trackers_new_start_time,
    )
    second_time_tracker_actual = TimeTracker.objects.get_or_none(status=TimeTrackerStatuses.IN_PROGRESS)
    second_start_tracker_actual_start_time = second_time_tracker_actual.start_time

    assert not result.data.get("success")
    assert result.data.get("errors")[0].get("attr") == "start_time"
    assert second_start_tracker_actual_start_time == second_time_tracker.start_time

    # Change start time for second tracker to 11:00
    second_time_trackers_new_start_time = {"start_time": second_time_tracker.start_time - datetime.timedelta(hours=1)}
    result = api_client.patch(
        reverse("time_tracker-detail", kwargs={"pk": second_time_tracker.id}),
        data=second_time_trackers_new_start_time,
    )
    second_time_tracker_actual = TimeTracker.objects.get_or_none(status=TimeTrackerStatuses.IN_PROGRESS)
    second_start_tracker_actual_start_time = second_time_tracker_actual.start_time

    assert result.data.get("success")
    assert second_start_tracker_actual_start_time == second_time_trackers_new_start_time.get("start_time")

@pytest.mark.django_db
@pytest.mark.freeze_time("2023-06-05 10:00:00")
def test_handle_start_time_not_gt_time_now(api_client, super_user, freezer):
    fill_up_statuses()

    api_client.force_authenticate(super_user)

    # Create Task with Department and User
    statuses = Status.objects.filter(name__in=[BaseStatuses.WAITING.name, BaseStatuses.IN_PROGRESS.name])
    department_data = {"name": "test_department", "statuses": [statuses[0].id, statuses[1].id]}
    department = api_client.post(reverse("department-list"), data=department_data)
    department_id = department.data.get("data")[0].get("id")

    assert department.data.get("success")

    user = api_client.patch(
        reverse("account-detail", kwargs={"pk": super_user.id}),
        data={"department": department_id},
    )

    assert user.data.get("success")

    task_data = {
        "name": "M-37-103-А",
        "scale": "50",
        "change_time_estimate": 50,
        "correct_time_estimate": 25,
        "otk_time_estimate": 15,
        "quarter": 1,
        "category": "some category",
        "user": user.data.get("data")[0].get("id"),
        "department": department_id,
        "primary_department": department_id,
    }

    task = api_client.post(reverse("task-list"), data=task_data, format='json')

    assert task.data.get("success")

    # Get First Time Tracker and try to change Start Time to 11:00

    first_time_tracker = TimeTracker.objects.filter(status=TimeTrackerStatuses.IN_PROGRESS).first()
    first_time_tracker_new_start_time = {"start_time": first_time_tracker.start_time + datetime.timedelta(hours=1)}
    result = api_client.patch(
        reverse("time_tracker-detail", kwargs={"pk": first_time_tracker.id}),
        data=first_time_tracker_new_start_time,
    )

    first_time_tracker_actual = TimeTracker.objects.get_or_none(status=TimeTrackerStatuses.IN_PROGRESS)
    first_time_tracker_actual_start_time = first_time_tracker_actual.start_time

    assert not result.data.get("success")
    assert result.data.get("errors")[0].get("attr") == "previous_tracker"
    assert first_time_tracker_actual_start_time == first_time_tracker.start_time

    # Change Fake time by 1 hour (11:00)
    hours_passed = 1
    freezer.move_to(
        datetime.datetime.now() + datetime.timedelta(hours=hours_passed)
    )

    # Create Second Time Tracker by updating task status to IN_PROGRESS
    all_tasks = api_client.get(reverse("task-list"))
    task_obj_id = all_tasks.data.get("data")[0].get("id")
    status_progress = Status.objects.get_or_none(name=BaseStatuses.IN_PROGRESS.name)
    new_task_status = {"status": status_progress.id}
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task_obj_id}),
        data=new_task_status,
        format="json",
    )

    assert result.data.get("success")

    # Get Second TT
    second_time_tracker = TimeTracker.objects.get_or_none(status=TimeTrackerStatuses.IN_PROGRESS.name)

    # Change Start time for Second TT more than time.now
    second_time_tracker_new_start_time = {"start_time": datetime.datetime.now() + datetime.timedelta(hours=1)}
    result = api_client.patch(
        reverse("time_tracker-detail", kwargs={"pk": second_time_tracker.id}),
        data=second_time_tracker_new_start_time,
    )
    second_time_tracker_actual = TimeTracker.objects.get_or_none(status=TimeTrackerStatuses.IN_PROGRESS)
    second_start_tracker_actual_start_time = second_time_tracker_actual.start_time

    assert not result.data.get("success")
    assert result.data.get("errors")[0].get("attr") == "start_time"
    assert second_start_tracker_actual_start_time == second_time_tracker.start_time

    # Test change Start time for TT more than End time
    # Change Fake time by 1 hour (12:00)
    freezer.move_to(
        datetime.datetime.now() + datetime.timedelta(hours=hours_passed)
    )

    # Change task status to Waiting (this will create Third TT)
    status_waiting = Status.objects.get_or_none(name=BaseStatuses.WAITING.name)
    new_task_status = {"status": status_waiting.id}
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task_obj_id}),
        data=new_task_status,
        format="json",
    )

    assert result.data.get("success")

    # Change Fake time by 1 hour (to 13:00)
    freezer.move_to(
        datetime.datetime.now() + datetime.timedelta(hours=hours_passed)
    )

    # Change Start time for Second TT more than End time
    second_time_tracker = TimeTracker.objects.filter(status=TimeTrackerStatuses.DONE.name).last()
    second_time_tracker_new_start_time = {"start_time": second_time_tracker.end_time + datetime.timedelta(hours=1)}
    result = api_client.patch(
        reverse("time_tracker-detail", kwargs={"pk": second_time_tracker.id}),
        data=second_time_tracker_new_start_time,
    )
    second_time_tracker_actual = TimeTracker.objects.filter(status=TimeTrackerStatuses.DONE.name).last()

    assert not result.data.get("success")
    assert result.data.get("errors")[0].get("attr") == "start_time"
    assert second_time_tracker_actual.start_time == second_time_tracker.start_time

@pytest.mark.django_db
@pytest.mark.freeze_time("2023-06-05 10:00:00")
def test_tt_end_time_not_gt_next_tt_end_time(api_client, super_user, freezer):
    fill_up_statuses()

    api_client.force_authenticate(super_user)

    # Create Task with Department and User
    statuses = Status.objects.filter(name__in=[BaseStatuses.WAITING.name, BaseStatuses.IN_PROGRESS.name])
    department_data = {"name": "test_department", "statuses": [statuses[0].id, statuses[1].id]}
    department = api_client.post(reverse("department-list"), data=department_data)
    department_id = department.data.get("data")[0].get("id")

    assert department.data.get("success")

    user = api_client.patch(
        reverse("account-detail", kwargs={"pk": super_user.id}),
        data={"department": department_id},
    )

    assert user.data.get("success")

    task_data = {
        "name": "M-37-103-А",
        "scale": "50",
        "change_time_estimate": 50,
        "correct_time_estimate": 25,
        "otk_time_estimate": 15,
        "quarter": 1,
        "category": "some category",
        "user": user.data.get("data")[0].get("id"),
        "department": department_id,
        "primary_department": department_id,
    }

    task = api_client.post(reverse("task-list"), data=task_data, format='json')

    assert task.data.get("success")

    # Change Fake time by 1 hour (11:00)
    hours_passed = 1
    freezer.move_to(
        datetime.datetime.now() + datetime.timedelta(hours=hours_passed)
    )

    # Create Second Time Tracker by updating task status to IN_PROGRESS
    all_tasks = api_client.get(reverse("task-list"))
    task_obj_id = all_tasks.data.get("data")[0].get("id")
    status_progress = Status.objects.get_or_none(name=BaseStatuses.IN_PROGRESS.name)
    new_task_status = {"status": status_progress.id}
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task_obj_id}),
        data=new_task_status,
        format="json",
    )

    assert result.data.get("success")

    # Change Fake time by 1 hour (12:00)
    freezer.move_to(
        datetime.datetime.now() + datetime.timedelta(hours=hours_passed)
    )

    # Create Third Time tracker by updating task status to Waiting
    status_waiting = Status.objects.get_or_none(name=BaseStatuses.WAITING.name)
    new_task_status = {"status": status_waiting.id}
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task_obj_id}),
        data=new_task_status,
        format="json",
    )

    assert result.data.get("success")

    # Change End time for First TT more than End time of Second TT
    first_tt = TimeTracker.objects.filter(status=TimeTrackerStatuses.DONE.name).first()
    second_tt = TimeTracker.objects.filter(status=TimeTrackerStatuses.DONE.name).last()

    first_tt_new_end_time = {"end_time": second_tt.end_time + datetime.timedelta(hours=1)}
    result = api_client.patch(
        reverse("time_tracker-detail", kwargs={"pk": first_tt.id}),
        data=first_tt_new_end_time,
    )
    first_tt_actual = TimeTracker.objects.filter(status=TimeTrackerStatuses.DONE.name).first()

    assert not result.data.get("success")
    assert result.data.get("errors")[0].get("attr") == "end_time"
    assert first_tt_actual.end_time == first_tt.end_time

    # Change End time for Second TT less than Start time of Second TT
    second_tt_new_end_time = {"end_time": second_tt.start_time - datetime.timedelta(hours=1)}
    result = api_client.patch(
        reverse("time_tracker-detail", kwargs={"pk": second_tt.id}),
        data=second_tt_new_end_time,
    )
    second_tt_actual = TimeTracker.objects.filter(status=TimeTrackerStatuses.DONE.name).last()

    assert not result.data.get("success")
    assert result.data.get("errors")[0].get("attr") == "end_time"
    assert second_tt_actual.end_time == second_tt.end_time
