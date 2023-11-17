import datetime

import pytest
from rest_framework.reverse import reverse

from api.models import TimeTrackerStatuses, TimeTracker, Statuses
from kanban.tasks import update_task_time_in_progress


@pytest.mark.django_db
@pytest.mark.freeze_time("2023-06-05 09:00:00")
def test_CRUD_time_tracker_ok(api_client, super_user, freezer):
    

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
        "scale": "50",
        "editing_time_estimate": 50,
        "correcting_time_estimate": 25,
        "tc_time_estimate": 15,
        "quarter": 1,
        "category": 3,
        "user": user.data.get("data")[0].get("id"),
        "department": department_id,
    }

    task = api_client.post(reverse("task-list"), data=task_data, format='json')
    assert task.data.get("success")
    task_id = task.data.get("data")[0].get("id")
    task_department = task.data.get("data")[0].get("department")

    TimeTracker.objects.all().delete()  # Delete all TimeTracker objects, cause one with status Waiting creates on creating Task

    # test create
    time_tracker_data = {
        "task": task_id,
        "user": user.data.get("data")[0].get("id"),
        'task_status': task.data['data'][0]['status'],
        "start_time": datetime.datetime.now(),
        "task_department": task_department,
    }

    result = api_client.post(reverse("time_tracker-list"), data=time_tracker_data)

    assert result.data.get("success")
    assert not result.data.get("errors")
    assert result.data.get("data_len") == 1
    assert result.data.get("message") == "Created"

    all_time_trackers = api_client.get(f'{reverse("time_tracker-list")}?status={TimeTrackerStatuses.IN_PROGRESS.value}')

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
        "scale": "50",
        "editing_time_estimate": 50,
        "correcting_time_estimate": 25,
        "tc_time_estimate": 15,
        "quarter": 1,
        "category": 3,
        "user": user.data.get("data")[0].get("id"),
        "department": department_id,
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

    # update task status to EDITING
    all_tasks = api_client.get(reverse("task-list"))
    task_obj_id = all_tasks.data.get("data")[0].get("id")
    new_task_status = {"status": Statuses.EDITING.value}
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
    

    api_client.force_authenticate(super_user)

    # Create Task with Department and User
    department_data = {"name": "test_department"}
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
        "editing_time_estimate": 50,
        "correcting_time_estimate": 25,
        "tc_time_estimate": 15,
        "quarter": 1,
        "category": 3,
        "user": user.data.get("data")[0].get("id"),
        "department": department_id,
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

    # Create Second Time Tracker by updating task status to EDITING
    all_tasks = api_client.get(reverse("task-list"))
    task_obj_id = all_tasks.data.get("data")[0].get("id")
    new_task_status = {"status": Statuses.EDITING.value}
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task_obj_id}),
        data=new_task_status,
        format="json",
    )

    assert result.data.get("success")

    # Get Second TT
    second_time_tracker = TimeTracker.objects.get_or_none(status=TimeTrackerStatuses.IN_PROGRESS.value)

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
    new_task_status = {"status": Statuses.EDITING_QUEUE.value}
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
    second_time_tracker = TimeTracker.objects.filter(status=TimeTrackerStatuses.DONE.value).last()
    second_time_tracker_new_start_time = {"start_time": second_time_tracker.end_time + datetime.timedelta(hours=1)}
    result = api_client.patch(
        reverse("time_tracker-detail", kwargs={"pk": second_time_tracker.id}),
        data=second_time_tracker_new_start_time,
    )
    second_time_tracker_actual = TimeTracker.objects.filter(status=TimeTrackerStatuses.DONE.value).last()

    assert not result.data.get("success")
    assert result.data.get("errors")[0].get("attr") == "start_time"
    assert second_time_tracker_actual.start_time == second_time_tracker.start_time


@pytest.mark.django_db
@pytest.mark.freeze_time("2023-06-05 10:00:00")
def test_tt_end_time_not_gt_next_tt_end_time(api_client, super_user, freezer):
    

    api_client.force_authenticate(super_user)

    # Create Task with Department and User
    department_data = {"name": "test_department"}
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
        "editing_time_estimate": 50,
        "correcting_time_estimate": 25,
        "tc_time_estimate": 15,
        "quarter": 1,
        "category": 3,
        "user": user.data.get("data")[0].get("id"),
        "department": department_id,
    }

    task = api_client.post(reverse("task-list"), data=task_data, format='json')

    assert task.data.get("success")

    # Change Fake time by 1 hour (11:00)
    hours_passed = 1
    freezer.move_to(
        datetime.datetime.now() + datetime.timedelta(hours=hours_passed)
    )

    # Create Second Time Tracker by updating task status to EDITING
    all_tasks = api_client.get(reverse("task-list"))
    task_obj_id = all_tasks.data.get("data")[0].get("id")
    new_task_status = {"status": Statuses.EDITING.value}
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
    new_task_status = {"status": Statuses.EDITING_QUEUE.value}
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task_obj_id}),
        data=new_task_status,
        format="json",
    )

    assert result.data.get("success")

    # Change End time for First TT more than End time of Second TT
    first_tt = TimeTracker.objects.filter(status=TimeTrackerStatuses.DONE.value).first()
    second_tt = TimeTracker.objects.filter(status=TimeTrackerStatuses.DONE.value).last()

    first_tt_new_end_time = {"end_time": second_tt.end_time + datetime.timedelta(hours=1)}
    result = api_client.patch(
        reverse("time_tracker-detail", kwargs={"pk": first_tt.id}),
        data=first_tt_new_end_time,
    )
    first_tt_actual = TimeTracker.objects.filter(status=TimeTrackerStatuses.DONE.value).first()

    assert not result.data.get("success")
    assert result.data.get("errors")[0].get("attr") == "end_time"
    assert first_tt_actual.end_time == first_tt.end_time

    # Change End time for Second TT less than Start time of Second TT
    second_tt_new_end_time = {"end_time": second_tt.start_time - datetime.timedelta(hours=1)}
    result = api_client.patch(
        reverse("time_tracker-detail", kwargs={"pk": second_tt.id}),
        data=second_tt_new_end_time,
    )
    second_tt_actual = TimeTracker.objects.filter(status=TimeTrackerStatuses.DONE.value).last()

    assert not result.data.get("success")
    assert result.data.get("errors")[0].get("attr") == "end_time"
    assert second_tt_actual.end_time == second_tt.end_time

@pytest.mark.django_db
@pytest.mark.freeze_time("2023-06-05 10:00:00")
def test_handle_update_inside_success(api_client, super_user, freezer):

    api_client.force_authenticate(super_user)

    # Create Task with Department and User
    department_data = {"name": "test_department"}
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
        "editing_time_estimate": 50,
        "correcting_time_estimate": 25,
        "tc_time_estimate": 15,
        "quarter": 1,
        "category": 3,
        "user": user.data.get("data")[0].get("id"),
        "department": department_id,
    }

    task = api_client.post(reverse("task-list"), data=task_data, format='json')

    assert task.data.get("success")

    # Change Fake time by 1 hour (11:00)
    hours_passed = 1
    freezer.move_to(
        datetime.datetime.now() + datetime.timedelta(hours=hours_passed)
    )

    # Create Second Time Tracker by updating task status to EDITING
    all_tasks = api_client.get(reverse("task-list"))
    task_obj_id = all_tasks.data.get("data")[0].get("id")
    new_task_status = {"status": Statuses.EDITING.value}
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
    new_task_status = {"status": Statuses.EDITING_QUEUE.value}
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task_obj_id}),
        data=new_task_status,
        format="json",
    )

    assert result.data.get("success")

    # Change Fake time by 1 hour (13:00)
    freezer.move_to(
        datetime.datetime.now() + datetime.timedelta(hours=hours_passed)
    )

    # Change start and end time for Second Time tracker ><
    second_tt = TimeTracker.objects.filter(status=TimeTrackerStatuses.DONE.value).last()
    second_tt_new_data = {
        "start_time": second_tt.start_time + datetime.timedelta(minutes=20),
        "end_time": second_tt.end_time - datetime.timedelta(minutes=20),
    }

    result = api_client.patch(
        reverse("time_tracker-detail", kwargs={"pk": second_tt.id}),
        data=second_tt_new_data,
    )

    status_in_progress = Status.objects.get_or_none(name=Statuses.EDITING.value)
    second_tt_actual = TimeTracker.objects.get_or_none(task_status=status_in_progress)

    # After updating THIS timetracker time, we will have 2 new timetrackers on the left and on the right side from THIS timetracker.
    expected_tts_count = 5

    assert result.data.get("success")
    assert second_tt_actual.start_time == second_tt_new_data.get("start_time")
    assert second_tt_actual.end_time == second_tt_new_data.get("end_time")
    assert len(TimeTracker.objects.all()) == expected_tts_count

@pytest.mark.django_db
@pytest.mark.freeze_time("2023-06-05 10:00:00")
def test_handle_update_outside_success(api_client, super_user, freezer):

    api_client.force_authenticate(super_user)

    # Create Task with Department and User
    department_data = {"name": "test_department"}
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
        "editing_time_estimate": 50,
        "correcting_time_estimate": 25,
        "tc_time_estimate": 15,
        "quarter": 1,
        "category": 3,
        "user": user.data.get("data")[0].get("id"),
        "department": department_id,
    }

    task = api_client.post(reverse("task-list"), data=task_data, format='json')

    assert task.data.get("success")

    # Change Fake time by 1 hour (11:00)
    hours_passed = 1
    freezer.move_to(
        datetime.datetime.now() + datetime.timedelta(hours=hours_passed)
    )

    # Create Second Time Tracker by updating task status to EDITING
    all_tasks = api_client.get(reverse("task-list"))
    task_obj_id = all_tasks.data.get("data")[0].get("id")
    new_task_status = {"status": Statuses.EDITING.value}
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
    new_task_status = {"status": Statuses.EDITING_QUEUE.value}
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task_obj_id}),
        data=new_task_status,
        format="json",
    )

    assert result.data.get("success")

    # Change Fake time by 1 hour (13:00)
    freezer.move_to(
        datetime.datetime.now() + datetime.timedelta(hours=hours_passed)
    )

    # Change start and end time for Second Time tracker <>
    second_tt = TimeTracker.objects.filter(status=TimeTrackerStatuses.DONE.value).last()
    second_tt_new_data = {
        "start_time": second_tt.start_time - datetime.timedelta(minutes=20),
        "end_time": second_tt.end_time + datetime.timedelta(minutes=20),
    }

    result = api_client.patch(
        reverse("time_tracker-detail", kwargs={"pk": second_tt.id}),
        data=second_tt_new_data,
    )

    second_tt_actual = TimeTracker.objects.filter(status=TimeTrackerStatuses.DONE.value).last()
    expected_tts_count = 3

    assert result.data.get("success")
    assert second_tt_actual.start_time == second_tt_new_data.get("start_time")
    assert second_tt_actual.end_time == second_tt_new_data.get("end_time")
    assert len(TimeTracker.objects.all()) == expected_tts_count

@pytest.mark.django_db
@pytest.mark.freeze_time("2023-06-05 10:00:00")
def test_update_time_trackers_hours(api_client, super_user, freezer):

    api_client.force_authenticate(super_user)

    # Create Task with Department and User
    department_data = {"name": "test_department"}
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
        "editing_time_estimate": 50,
        "correcting_time_estimate": 25,
        "tc_time_estimate": 15,
        "quarter": 1,
        "category": 3,
        "user": user.data.get("data")[0].get("id"),
        "department": department_id,
    }

    task = api_client.post(reverse("task-list"), data=task_data, format='json')

    assert task.data.get("success")

    first_tt = TimeTracker.objects.get_or_none(status=TimeTrackerStatuses.IN_PROGRESS.value)

    # Changing Time by 1 hour (11:00)
    hours_passed = 1
    freezer.move_to(
        datetime.datetime.now() + datetime.timedelta(hours=hours_passed)
    )

    # Update Time Trackers Time
    update_task_time_in_progress()

    first_tt_updated = TimeTracker.objects.get_or_none(status=TimeTrackerStatuses.IN_PROGRESS.value)

    assert first_tt.hours + hours_passed == first_tt_updated.hours

    task_2 = api_client.post(reverse("task-list"), data=task_data, format='json')

    assert task_2.data.get("success")

    # Test update TTs time for 2 tasks
    first_tt_task_2 = TimeTracker.objects.filter(status=TimeTrackerStatuses.IN_PROGRESS.value).last()

    # Changing Time by 2 hour (13:00)
    hours_passed = 2
    freezer.move_to(
        datetime.datetime.now() + datetime.timedelta(hours=hours_passed)
    )

    # Update Time Trackers Time
    update_task_time_in_progress()

    first_tt_task_2_updated = TimeTracker.objects.filter(status=TimeTrackerStatuses.IN_PROGRESS.value).last()

    assert first_tt_task_2.hours + hours_passed == first_tt_task_2_updated.hours

    # Test update TTs time in Lunch and after business hours AND in Status DONE

    # in Status DONE
    # Create Second Time Tracker for Task_1 by updating task status to EDITING
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
        data={"status": Statuses.EDITING.value},
        format="json",
    )


    assert result.data.get("success")

    tt_1_task_1, tt_2_task_1 = TimeTracker.objects.filter(task_id=task.data.get("data")[0].get("id"))
    tt_1_task_2 = TimeTracker.objects.get_or_none(task_id=task_2.data.get("data")[0].get("id"))

    lunch_time = 1
    non_working_hours = 2

    # Changing Time by 7 hour (20:00)
    hours_passed = 7
    freezer.move_to(
        datetime.datetime.now() + datetime.timedelta(hours=hours_passed)
    )

    # Update Time Trackers Time
    update_task_time_in_progress()

    tt_1_task_1_updated, tt_2_task_1_updated = TimeTracker.objects.filter(task_id=task.data.get("data")[0].get("id"))
    tt_1_task_2_updated = TimeTracker.objects.get_or_none(task_id=task_2.data.get("data")[0].get("id"))

    assert tt_1_task_1.hours == tt_1_task_1_updated.hours
    assert tt_2_task_1.hours + hours_passed - lunch_time - non_working_hours == tt_2_task_1_updated.hours
    assert tt_1_task_2.hours + hours_passed - lunch_time - non_working_hours == tt_1_task_2_updated.hours


