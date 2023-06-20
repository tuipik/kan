import pytest
from rest_framework.reverse import reverse

from api.models import TaskStatuses, TimeTracker
from conftest import create_user_with_department, create_task


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
    user, department = create_user_with_department()
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
