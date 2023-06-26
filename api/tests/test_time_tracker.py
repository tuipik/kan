import pytest
from rest_framework.reverse import reverse

from api.models import TimeTrackerStatuses, TimeTracker


@pytest.mark.django_db
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
        "change_time_estimate": 50,
        "correct_time_estimate": 25,
        "otk_time_estimate": 15,
        "quarter": 1,
        "category": "some category",
        "user": user.data.get("data")[0].get("id"),
        "department": department_id,
    }

    task = api_client.post(reverse("task-list"), data=task_data)
    assert task.data.get("success")
    task_id = task.data.get("data")[0].get("id")

    # test create
    time_tracker_data = {
        "task": task_id,
        "user": user.data.get("data")[0].get("id"),
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
    assert all_time_trackers.data.get("data")[0].get("user") == time_tracker_data.get(
        "user"
    )
    assert not all_time_trackers.data.get("data")[0].get("end_time")
    assert all_time_trackers.data.get("data")[0].get("hours") == 0
    assert (
        all_time_trackers.data.get("data")[0].get("status")
        == TimeTrackerStatuses.IN_PROGRESS
    )

    # test put
    time_tracker_obj_id = all_time_trackers.data.get("data")[0].get("id")
    time_tracker_data["status"] = TimeTrackerStatuses.DONE

    result = api_client.put(
        reverse("time_tracker-detail", kwargs={"pk": time_tracker_obj_id}),
        data=time_tracker_data,
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
