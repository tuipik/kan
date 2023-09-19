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
    }

    result = api_client.post(reverse("time_tracker-list"), data=time_tracker_data)

    assert result.data.get("success")
    assert not result.data.get("errors")
    assert result.data.get("data_len") == 1
    assert result.data.get("message") == "Created"

    all_time_trackers = api_client.get(reverse("time_tracker-list"))

    assert all_time_trackers.data.get("data_len") == 1
    assert all_time_trackers.data.get("data")[0].get("task") == time_tracker_data.get(
        "task"
    )
    assert all_time_trackers.data.get("data")[0].get("user").get(
        "id"
    ) == time_tracker_data.get("user")
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
