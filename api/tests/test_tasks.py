import datetime
import pytest
from rest_framework.reverse import reverse

from api.CONSTANTS import TASK_NAME_RULES
from api.models import TimeTracker, TimeTrackerStatuses, Statuses
from api.utils import fill_up_statuses
from conftest import create_user_with_department, create_task, default_user_data
from kanban.settings import workday_time, launch_time


@pytest.mark.django_db
def test_task_name_correct(api_client, super_user):
    fill_up_statuses()
    api_client.force_authenticate(super_user)

    statuses = Status.objects.filter(name__in=[Statuses.EDITING_QUEUE.value, Statuses.EDITING.value])
    department_data = {"name": "test_department", "statuses": [statuses[0].id, statuses[1].id]}
    department = api_client.post(reverse("department-list"), data=department_data)
    department_id = department.data.get("data")[0].get("id")
    task_data = {
        "name": "M-37-103-А-а",
        "scale": 25,
        "editing_time_estimate": 50,
        "correcting_time_estimate": 25,
        "tc_time_estimate": 15,
        "quarter": 1,
        "category": 3,
        "user": None,
        "department": department_id,
    }

    result = api_client.post(reverse("task-list"), data=task_data, format="json")

    assert result.data.get("success")
    assert not result.data.get("errors")


@pytest.mark.django_db
def test_task_name_incorrect(api_client, super_user):
    fill_up_statuses()
    api_client.force_authenticate(super_user)

    statuses = Status.objects.filter(name__in=[Statuses.EDITING_QUEUE.value, Statuses.EDITING.value])
    department_data = {"name": "test_department", "statuses": [statuses[0].id, statuses[1].id]}
    department = api_client.post(reverse("department-list"), data=department_data)
    department_id = department.data.get("data")[0].get("id")
    # ROW_ERROR (1st letter cyrillic)
    task_data = {
        "name": "М-37-103-А-а",
        "scale": 25,
        "editing_time_estimate": 50,
        "correcting_time_estimate": 25,
        "tc_time_estimate": 15,
        "quarter": 1,
        "category": 3,
        "user": None,
        "department": department_id,
    }

    result = api_client.post(reverse("task-list"), data=task_data, format="json")

    assert not result.data.get("success")
    assert result.data.get("errors")
    assert result.data.get("errors")[0].get('detail') == TASK_NAME_RULES.get(25).get(0).get('error')

    # ROW_ERROR (first_letter_small)
    task_data["name"] = "m-37-103-А-а"
    result = api_client.post(reverse("task-list"), data=task_data, format="json")

    assert not result.data.get("success")
    assert result.data.get("errors")
    assert result.data.get("errors")[0].get('detail') == TASK_NAME_RULES.get(25).get(0).get('error')

    # ROW_ERROR (first_letter_out_of_range)
    task_data["name"] = "W-37-103-А-а"
    result = api_client.post(reverse("task-list"), data=task_data, format="json")

    assert not result.data.get("success")
    assert result.data.get("errors")
    assert result.data.get("errors")[0].get('detail') == TASK_NAME_RULES.get(25).get(0).get('error')

    # Test COLON_ERROR, THOUSANDS_ERROR, CYRILLIC_LETTERS_UP_ERROR, CYRILLIC_LETTERS_DOWN_ERROR
    task_data["name"] = "M-63-0-a-a"
    result = api_client.post(reverse("task-list"), data=task_data, format="json")

    assert not result.data.get("success")
    assert result.data.get("errors")
    assert result.data.get("errors")[0].get('detail') == TASK_NAME_RULES.get(25).get(1).get('error')
    assert result.data.get("errors")[1].get('detail') == TASK_NAME_RULES.get(25).get(2).get('error')
    assert result.data.get("errors")[2].get('detail') == TASK_NAME_RULES.get(25).get(3).get('error')
    assert result.data.get("errors")[3].get('detail') == TASK_NAME_RULES.get(25).get(4).get('error')

    # Test no ROMAN_ERROR
    task_data["name"] = "M-36-XIX"
    task_data["scale"] = 200
    result = api_client.post(reverse("task-list"), data=task_data, format="json")

    assert result.data.get("success")
    assert not result.data.get("errors")

    # Test ROMAN_ERROR
    task_data["name"] = "M-36-XXXIX"
    task_data["scale"] = 200
    result = api_client.post(reverse("task-list"), data=task_data, format="json")

    assert not result.data.get("success")
    assert result.data.get("errors")
    assert result.data.get("errors")[0].get('detail') == TASK_NAME_RULES.get(200).get(2).get('error')

@pytest.mark.django_db
def test_CRUD_tasks_ok(api_client, super_user):
    fill_up_statuses()
    api_client.force_authenticate(super_user)

    statuses = Status.objects.filter(name__in=[Statuses.EDITING_QUEUE.value, Statuses.EDITING.value])
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
        "scale": 50,
        "editing_time_estimate": 50,
        "correcting_time_estimate": 25,
        "tc_time_estimate": 15,
        "quarter": 1,
        "category": 3,
        "user": user.data.get("data")[0].get("id"),
        "department": department_id,
        "primary_department": department_id,
    }

    # test create
    result = api_client.post(reverse("task-list"), data=task_data, format="json")

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
    task_data["primary_department"] = task_data["department"]
    task_data["status"] = Status.objects.get(name=Statuses.EDITING.value).id

    result = api_client.put(
        reverse("task-detail", kwargs={"pk": task_obj_id}),
        data=task_data,
        format="json",
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
        format="json",
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
def test_user_already_has_task_in_progress(api_client, super_user, freezer):
    fill_up_statuses()

    api_client.force_authenticate(super_user)
    user_data = default_user_data(3)
    user_executant, department = create_user_with_department(next(user_data))
    task_data = {
        "name": "M-32-44-Г",
        "scale": 50,
        "editing_time_estimate": 50,
        "correcting_time_estimate": 25,
        "tc_time_estimate": 15,
        "quarter": 1,
        "category": 3,
        "user": None,
        "department": department.id,
    }

    task_1 = api_client.post(reverse("task-list"), data=task_data, format="json")
    task_1_in_progress = api_client.patch(
        reverse("task-detail", kwargs={"pk": task_1.data.get("data")[0].get("id")}),
        data={"user": user_executant.id, "status": Status.objects.get_or_none(name="EDITING").id},
        format="json",
    )
    task_data["name"] = "M-32-44-Б"
    task_2 = api_client.post(reverse("task-list"), data=task_data, format="json")
    task_2_in_progress = api_client.patch(
        reverse("task-detail", kwargs={"pk": task_2.data.get("data")[0].get("id")}),
        data={"user": user_executant.id, "status": Status.objects.get_or_none(name="EDITING").id},
        format="json",
    )
    assert not task_2_in_progress.data.get("success")
    assert task_2_in_progress.data.get("errors")


@pytest.mark.django_db
def test_create_time_tracker_on_change_task_in_progress(
    api_client, super_user, freezer
):
    fill_up_statuses()

    api_client.force_authenticate(super_user)
    user_data = default_user_data(1)
    user, department = create_user_with_department(next(user_data))
    task = create_task(user=user, department=department)
    a1 = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"user": user.id, "status": Status.objects.get_or_none(name="EDITING").id}, format="json"
    )
    # the second run update with status EDITING is to test, that only 1 TimeTracker can be IN_PROGRESS at one time
    # and should change status to idle first
    a2 = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"user": user.id, "status": Status.objects.get_or_none(name="EDITING").id}, format="json"
    )

    time_trackers = TimeTracker.objects.filter(status=TimeTrackerStatuses.IN_PROGRESS)
    assert time_trackers.count() == 1
    assert time_trackers[0].task.id == task.id
    assert time_trackers[0].user.id == user.id
    assert time_trackers[0].status == TimeTrackerStatuses.IN_PROGRESS.value

    api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"status": Status.objects.get_or_none(name="EDITING_QUEUE").id}, format="json"
    )


@pytest.mark.django_db
@pytest.mark.freeze_time("2023-06-05 09:00:00")
def test_change_status_less_4_hours(api_client, super_user, freezer):
    fill_up_statuses()

    user_data = default_user_data(1)
    user, department = create_user_with_department(next(user_data))
    task = create_task(user=user, department=department)

    api_client.force_authenticate(super_user)

    # task EDITING creates time_tracker
    api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"status": Status.objects.get_or_none(name="EDITING").id}, format="json"
    )

    hours_passed = 3
    freezer.move_to(datetime.datetime.now() + datetime.timedelta(hours=hours_passed))

    # task DONE updates time_tracker with status DONE
    api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"status": Status.objects.get_or_none(name="DONE").id}, format="json"
    )
    time_trackers = api_client.get(reverse("time_tracker-list"))

    assert time_trackers.data.get("data")[1].get("status") == TimeTrackerStatuses.DONE
    assert time_trackers.data.get("data")[1].get("hours") == hours_passed
    assert time_trackers.data.get("data")[1].get("end_time")


@pytest.mark.django_db
@pytest.mark.freeze_time("2023-06-05 09:00:00")
def test_change_status_more_4_hours(api_client, super_user, freezer):
    fill_up_statuses()

    user_data = default_user_data(1)
    user, department = create_user_with_department(next(user_data))
    task = create_task(user=user, department=department)

    api_client.force_authenticate(super_user)

    # task EDITING creates time_tracker
    api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"status": Status.objects.get_or_none(name="EDITING").id}, format="json"
    )

    hours_passed = 5
    freezer.move_to(datetime.datetime.now() + datetime.timedelta(hours=hours_passed))

    # task DONE updates time_tracker with status DONE
    api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"status": Status.objects.get_or_none(name="DONE").id}, format="json"
    )
    time_trackers = api_client.get(reverse("time_tracker-list"))

    assert time_trackers.data.get("data")[1].get("status") == TimeTrackerStatuses.DONE
    assert time_trackers.data.get("data")[1].get("hours") == hours_passed - launch_time
    assert time_trackers.data.get("data")[1].get("end_time")


@pytest.mark.django_db
@pytest.mark.freeze_time("2023-06-05 09:00:00")
def test_change_status_more_8_hours(api_client, super_user, freezer):
    fill_up_statuses()

    user_data = default_user_data(1)
    user, department = create_user_with_department(next(user_data))
    task = create_task(user=user, department=department)

    api_client.force_authenticate(super_user)

    # task EDITING creates time_tracker
    api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"status": Status.objects.get_or_none(name="EDITING").id}, format="json"
    )

    hours_passed = 10
    freezer.move_to(datetime.datetime.now() + datetime.timedelta(hours=hours_passed))

    # task DONE updates time_tracker with status DONE
    api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"status": Status.objects.get_or_none(name="DONE").id}, format="json"
    )
    time_trackers = api_client.get(reverse("time_tracker-list"))

    assert time_trackers.data.get("data")[1].get("status") == TimeTrackerStatuses.DONE
    assert time_trackers.data.get("data")[1].get("hours") == workday_time
    assert time_trackers.data.get("data")[1].get("end_time")

@pytest.mark.django_db
def test_check_user_is_department_member_of_task_department(api_client, super_user):
    fill_up_statuses()
    default_user_num = 2
    api_client.force_authenticate(super_user)

    # create users with departments
    users_data = default_user_data(default_user_num)
    user_1, dep_1 = create_user_with_department(next(users_data), dep_name="Dep_1")
    user_2, dep_2 = create_user_with_department(next(users_data), dep_name="Dep_2")

    # create task
    task_data = {
        "name": "M-37-103-А",
        "scale": 50,
        "editing_time_estimate": 50,
        "correcting_time_estimate": 25,
        "tc_time_estimate": 15,
        "quarter": 1,
        "category": 3,
        "user": None,
        "department": dep_1.id,
        "primary_department": dep_1.id,
    }
    task = api_client.post(reverse("task-list"), data=task_data, format="json")

    # update task
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
        data={"user": user_1.id},
        format="json",
    )

    assert result.data.get("success")
    assert not result.data.get("errors")

    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
        data={"user": user_2.id},
        format="json",
    )

    assert not result.data.get("success")

@pytest.mark.django_db
def test_updating_task_status(api_client, super_user):
    fill_up_statuses()
    api_client.force_authenticate(super_user)
    default_user_num = 3

    # create user with department
    users_data = default_user_data(default_user_num)
    user_1, dep_1 = create_user_with_department(next(users_data), dep_name="Dep_1")
    user_2, dep_2 = create_user_with_department(next(users_data), dep_name="Dep_2")
    user_3, dep_3 = create_user_with_department(next(users_data), dep_name="Dep_3")

    # Add Statuses for departments

    statuses_for_custom_deps = Status.objects.filter(name__in=[Statuses.EDITING_QUEUE.value, Statuses.EDITING.value])
    statuses_for_correcting_deps = Status.objects.filter(name__in=[Statuses.CORRECTING_QUEUE.value, Statuses.CORRECTING.value])

    result = api_client.patch(
        reverse("department-detail", kwargs={"pk": dep_1.id}),
        data={"is_verifier": True,
              "statuses": [statuses_for_custom_deps[0].id,  statuses_for_custom_deps[1].id]
              },
    )

    assert result.data.get("success")

    result = api_client.patch(
        reverse("department-detail", kwargs={"pk": dep_2.id}),
        data={"is_verifier": True,
              "statuses": [statuses_for_custom_deps[0].id,  statuses_for_custom_deps[1].id]
              },
    )

    assert result.data.get("success")

    result = api_client.patch(
        reverse("department-detail", kwargs={"pk": dep_3.id}),
        data={"is_verifier": True,
              "statuses": [statuses_for_correcting_deps[0].id, statuses_for_correcting_deps[1].id]
              },
    )

    assert result.data.get("success")

    # create task
    task_data = {
        "name": "M-37-103-А",
        "scale": 50,
        "editing_time_estimate": 50,
        "correcting_time_estimate": 25,
        "tc_time_estimate": 15,
        "quarter": 1,
        "category": 3,
        "user": user_1.id,
        "department": dep_1.id,
        "primary_department": dep_1.id,
    }
    task = api_client.post(reverse("task-list"), data=task_data, format="json")

    # Changing department by user (not-verifier to not-verifier) - Working only when User = None
    # update task
    api_client.logout()
    api_client.force_authenticate(user_1)

    # Changing task status inside department (from Waiting to In_Progress) -> department == primary_department
    new_task_status = Status.objects.get_or_none(name="EDITING").id
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
        data={"status": new_task_status},
        format="json",
    )

    assert result.data.get("success")
    assert result.data.get("department") == result.data.get("primary_department")

    # result = api_client.patch(
    #     reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
    #     data={"department": dep_2.id, "user": None},
    #     format="json",
    # )
    #
    # assert result.data.get("success")
    # assert not result.data.get("errors")

    # Changing task status to CORRECTING by user from not-verifier department - Error
    # result = api_client.patch(
    #     reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
    #     data={"user": user_3.id},
    #     format="json",
    # )
    #
    # assert result.data.get("success")

    # Changing status to Correcting by user from custom department -> user can't change to Correcting (only to Correcting_Queue)
    new_task_status = Status.objects.get_or_none(name="CORRECTING").id
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
        data={"status": new_task_status, "user": user_3.id},
        format="json",
    )

    assert not result.data.get("success")
    assert result.data.get("errors")[0].get("attr") == "status"

