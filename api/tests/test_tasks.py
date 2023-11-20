import datetime
import pytest
from rest_framework.reverse import reverse

from api.CONSTANTS import TASK_NAME_RULES
from api.models import TimeTracker, TimeTrackerStatuses, Statuses, UserRoles, Department
from conftest import create_user_with_department, create_task, default_user_data, create_default_user
from kanban.settings import workday_time, launch_time


@pytest.mark.django_db
def test_task_name_correct(api_client, super_user):

    api_client.force_authenticate(super_user)

    department_data = {"name": "test_department"}
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
    
    api_client.force_authenticate(super_user)

    department_data = {"name": "test_department"}
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
        "scale": 50,
        "editing_time_estimate": 50,
        "correcting_time_estimate": 25,
        "tc_time_estimate": 15,
        "quarter": 1,
        "category": 3,
        "user": user.data.get("data")[0].get("id"),
        "department": department_id,
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
    task_data["status"] = Statuses.EDITING.value

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
    

    api_client.force_authenticate(super_user)
    user_data = default_user_data(3, roles=[UserRoles.EDITOR.value])
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
        data={"user": user_executant.id, "status": Statuses.EDITING.value},
        format="json",
    )
    task_data["name"] = "M-32-44-Б"
    task_2 = api_client.post(reverse("task-list"), data=task_data, format="json")
    task_2_in_progress = api_client.patch(
        reverse("task-detail", kwargs={"pk": task_2.data.get("data")[0].get("id")}),
        data={"user": user_executant.id, "status": Statuses.EDITING.value},
        format="json",
    )
    assert not task_2_in_progress.data.get("success")
    assert task_2_in_progress.data.get("errors")


@pytest.mark.django_db
def test_create_time_tracker_on_change_task_in_progress(
    api_client, super_user, freezer
):

    api_client.force_authenticate(super_user)
    user_data = default_user_data(1, roles=[UserRoles.EDITOR.value])
    user, department = create_user_with_department(next(user_data))
    task = create_task(user=user, department=department)
    a1 = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"user": user.id, "status": Statuses.EDITING.value}, format="json"
    )
    # the second run update with status EDITING is to test, that only 1 TimeTracker can be IN_PROGRESS at one time
    # and should change status to idle first
    a2 = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"user": user.id, "status": Statuses.EDITING.value}, format="json"
    )

    time_trackers = TimeTracker.objects.filter(status=TimeTrackerStatuses.IN_PROGRESS)
    assert time_trackers.count() == 1
    assert time_trackers[0].task.id == task.id
    assert time_trackers[0].user.id == user.id
    assert time_trackers[0].status == TimeTrackerStatuses.IN_PROGRESS.value

    api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"status": Statuses.EDITING_QUEUE.value}, format="json"
    )


@pytest.mark.django_db
@pytest.mark.freeze_time("2023-06-05 09:00:00")
def test_change_status_less_4_hours(api_client, super_user, freezer):
    

    user_data = default_user_data(1, roles=[UserRoles.EDITOR.value])
    user, department = create_user_with_department(next(user_data))
    task = create_task(user=user, department=department)

    api_client.force_authenticate(super_user)

    # task EDITING creates time_tracker
    api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"status": Statuses.EDITING.value, "user": user.id}, format="json"
    )

    hours_passed = 3
    freezer.move_to(datetime.datetime.now() + datetime.timedelta(hours=hours_passed))

    # task DONE updates time_tracker with status DONE
    api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"status": Statuses.DONE.value}, format="json"
    )
    time_trackers = api_client.get(reverse("time_tracker-list"))

    assert time_trackers.data.get("data")[1].get("status") == TimeTrackerStatuses.DONE
    assert time_trackers.data.get("data")[1].get("hours") == hours_passed
    assert time_trackers.data.get("data")[1].get("end_time")


@pytest.mark.django_db
@pytest.mark.freeze_time("2023-06-05 09:00:00")
def test_change_status_more_4_hours(api_client, super_user, freezer):
    

    user_data = default_user_data(1, roles=[UserRoles.EDITOR.value])
    user, department = create_user_with_department(next(user_data))
    task = create_task(user=user, department=department)

    api_client.force_authenticate(super_user)

    # task EDITING creates time_tracker
    api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"status": Statuses.EDITING.value, "user": user.id}, format="json"
    )

    hours_passed = 5
    freezer.move_to(datetime.datetime.now() + datetime.timedelta(hours=hours_passed))

    # task DONE updates time_tracker with status DONE
    api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"status": Statuses.DONE.value}, format="json"
    )
    time_trackers = api_client.get(reverse("time_tracker-list"))

    assert time_trackers.data.get("data")[1].get("status") == TimeTrackerStatuses.DONE
    assert time_trackers.data.get("data")[1].get("hours") == hours_passed - launch_time
    assert time_trackers.data.get("data")[1].get("end_time")


@pytest.mark.django_db
@pytest.mark.freeze_time("2023-06-05 09:00:00")
def test_change_status_more_8_hours(api_client, super_user, freezer):
    

    user_data = default_user_data(1, roles=[UserRoles.EDITOR.value])
    user, department = create_user_with_department(next(user_data))
    task = create_task(user=user, department=department)

    api_client.force_authenticate(super_user)

    # task EDITING creates time_tracker
    api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"status": Statuses.EDITING.value, "user": user.id}, format="json"
    )

    hours_passed = 10
    freezer.move_to(datetime.datetime.now() + datetime.timedelta(hours=hours_passed))

    # task DONE updates time_tracker with status DONE
    api_client.patch(
        reverse("task-detail", kwargs={"pk": task.id}),
        data={"status": Statuses.DONE.value}, format="json"
    )
    time_trackers = api_client.get(reverse("time_tracker-list"))

    assert time_trackers.data.get("data")[1].get("status") == TimeTrackerStatuses.DONE
    assert time_trackers.data.get("data")[1].get("hours") == workday_time
    assert time_trackers.data.get("data")[1].get("end_time")

@pytest.mark.django_db
def test_check_user_is_department_member_of_task_department(api_client, super_user):
    
    api_client.force_authenticate(super_user)

    # create users with departments
    users_data = default_user_data(2, roles=[UserRoles.EDITOR.value, UserRoles.EDITOR.value])
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
    
    api_client.force_authenticate(super_user)
    default_user_num = 3

    # create user with department
    users_data = default_user_data(default_user_num, roles=[UserRoles.EDITOR.value, UserRoles.EDITOR.value, UserRoles.EDITOR.value])
    user_1, dep_1 = create_user_with_department(next(users_data), dep_name="Dep_1")
    user_2, dep_2 = create_user_with_department(next(users_data), dep_name="Dep_2")
    user_3, dep_3 = create_user_with_department(next(users_data), dep_name="Dep_3")

    # Add Statuses for departments

    result = api_client.patch(
        reverse("department-detail", kwargs={"pk": dep_1.id}),
        data={"is_verifier": True},
    )

    assert result.data.get("success")

    result = api_client.patch(
        reverse("department-detail", kwargs={"pk": dep_2.id}),
        data={"is_verifier": True},
    )

    assert result.data.get("success")

    result = api_client.patch(
        reverse("department-detail", kwargs={"pk": dep_3.id}),
        data={"is_verifier": True},
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
    new_task_status = Statuses.EDITING.value
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
        data={"status": new_task_status},
        format="json",
    )

    assert result.data.get("success")
    assert result.data.get("department") == result.data.get("primary_department")

    # Changing status to Correcting by user from custom department -> user can't change to Correcting (only to Correcting_Queue)
    new_task_status = Statuses.CORRECTING.value
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
        data={"status": new_task_status, "user": user_3.id},
        format="json",
    )

    assert not result.data.get("success")
    assert result.data.get("errors")[0].get("attr") == "status"


@pytest.mark.django_db
def test_changing_task_status_by_editor(api_client, super_user):

    """
    TestCase: Editor CAN'T change Task Status to Correcting (Error),
    TC_QUEUE (Error), TC (Error).
    Then: Editor CAN change Task Status to Editing, Correcting_Queue, Editing_queue
    """

    api_client.force_authenticate(super_user)

    # create user with department
    users_data = default_user_data(3,
                                   roles=[UserRoles.EDITOR.value, UserRoles.EDITOR.value, UserRoles.EDITOR.value])
    user_1, dep_1 = create_user_with_department(next(users_data), dep_name="Dep_1")

    # create task
    task_data = {
        "name": "M-37-103-А",
        "scale": 50,
        "editing_time_estimate": 50,
        "correcting_time_estimate": 25,
        "tc_time_estimate": 15,
        "quarter": 1,
        "user": user_1.id,
        "department": dep_1.id,
    }
    task = api_client.post(reverse("task-list"), data=task_data, format="json")

    # Login by user_1
    api_client.logout()
    api_client.force_authenticate(user_1)

    # (1) Change Task Status to Correcting by Editor (User_1) -> Error
    new_task_status = Statuses.CORRECTING.value
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
        data={"status": new_task_status},
        format="json",
    )

    assert not result.data.get("success")
    assert result.data.get("errors")[0].get("attr") == "status"


    # (2) Change Task Status to TC_QUEUE by Editor (User_1) -> Error
    new_task_status = Statuses.TC_QUEUE.value
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
        data={"status": new_task_status},
        format="json",
    )

    assert not result.data.get("success")
    assert result.data.get("errors")[0].get("attr") == "status"


    # (3) Change Task Status to TC by Editor (User_1) -> Error
    new_task_status = Statuses.TC.value
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
        data={"status": new_task_status},
        format="json",
    )

    assert not result.data.get("success")
    assert result.data.get("errors")[0].get("attr") == "status"


    # (4) Change Task Status to Editing by Editor (User_1) -> OK
    new_task_status = Statuses.EDITING.value
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
        data={"status": new_task_status},
        format="json",
    )

    assert result.data.get("success")
    assert not result.data.get("errors")

    # (5) Change Task Status to Correcting_Queue by Editor (User_1) -> OK
    new_task_status = Statuses.CORRECTING_QUEUE.value
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
        data={"status": new_task_status},
        format="json",
    )

    assert result.data.get("success")
    assert not result.data.get("errors")


    # (6) Change Task Status to Editing_Queue by Editor (User_1) -> OK
    new_task_status = Statuses.EDITING_QUEUE.value
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
        data={"status": new_task_status},
        format="json",
    )

    assert result.data.get("success")
    assert not result.data.get("errors")


@pytest.mark.django_db
def test_changing_users_by_changing_task_status(api_client, super_user):

    """
    TestCase: When Task Status changing to ..._Queue - user changing to NULL.
        BUT: if some user was involved in this task status - he will be automatically assigned to this task again.
    """

    api_client.force_authenticate(super_user)

    # create user with department
    users_data = default_user_data(2,
                                   roles=[UserRoles.EDITOR.value, UserRoles.CORRECTOR.value])
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
        "user": user_1.id,
        "department": dep_1.id,
    }
    task = api_client.post(reverse("task-list"), data=task_data, format="json")

    # Login by user_1
    api_client.logout()
    api_client.force_authenticate(user_1)

    # (1) Change Task Status to Editing by User_1 (Editor) -> OK
    new_task_status = Statuses.EDITING.value
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
        data={"status": new_task_status},
        format="json",
    )

    assert result.data.get("success")
    assert not result.data.get("errors")
    assert result.data.get("data")[0]["status"] == "EDITING"
    assert result.data.get("data")[0]["user"] == user_1.id


    # (2) Change Task Status to Correcting_Queue by User_1 (Editor) -> OK
    new_task_status = Statuses.CORRECTING_QUEUE.value
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
        data={"status": new_task_status},
        format="json",
    )

    assert result.data.get("success")
    assert not result.data.get("errors")
    assert result.data.get("data")[0]["status"] == "CORRECTING_QUEUE"
    assert result.data.get("data")[0]["user"] == None


    # (3) Change Task Status to Correcting by User_2 (Corrector) -> OK

    # Login by User_2
    api_client.logout()
    api_client.force_authenticate(user_2)

    # Change Task Status to Correcting
    new_task_status = Statuses.CORRECTING.value
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
        data={"status": new_task_status, "user": user_2.id},
        format="json",
    )

    assert result.data.get("success")
    assert not result.data.get("errors")
    assert result.data.get("data")[0]["status"] == "CORRECTING"
    assert result.data.get("data")[0]["user"] == user_2.id


    # (4) Change Task Status to Editing_Queue by User_2 (Corrector) -> OK

    # Change Task Status to Editing_Queue
    new_task_status = Statuses.EDITING_QUEUE.value
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
        data={"status": new_task_status},
        format="json",
    )

    assert result.data.get("success")
    assert not result.data.get("errors")
    assert result.data.get("data")[0]["status"] == "EDITING_QUEUE"
    assert result.data.get("data")[0]["user"] == user_1.id


@pytest.mark.django_db
def test_changing_statuses_by_corrector(api_client, super_user):

    """
    TestCase: User (corrector) changes statuses to Editing, Correcting Queue, Correcting and TC Queue -> Success.
    """

    api_client.force_authenticate(super_user)

    # create user with department
    users_data = default_user_data(2,
                                   roles=[UserRoles.EDITOR.value, UserRoles.CORRECTOR.value])
    user_1, dep_1 = create_user_with_department(next(users_data), dep_name="Dep_1")

    user_corrector_data = {
        "username": f"user_corrector",
        "first_name": f"default_f_name",
        "last_name": f"default_l_name",
        "password": "default_pass",
        "password2": "default_pass",
        "department": "",
        "role": UserRoles.CORRECTOR.value,
    }
    user_2 = create_default_user(user_corrector_data)
    user_2.department = Department.objects.get(id=1)
    user_2.save()

    # create task
    task_data = {
        "name": "M-37-103-А",
        "scale": 50,
        "editing_time_estimate": 50,
        "correcting_time_estimate": 25,
        "tc_time_estimate": 15,
        "quarter": 1,
        "user": user_1.id,
        "department": dep_1.id,
    }
    task = api_client.post(reverse("task-list"), data=task_data, format="json")

    # Login by user_2
    api_client.logout()
    api_client.force_authenticate(user_2)

    # (1) Change Task Status to Editing by User_2 (corrector) -> OK
    new_task_status = Statuses.EDITING.value
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
        data={"status": new_task_status, "user": user_2.id},
        format="json",
    )

    assert result.data.get("success")
    assert not result.data.get("errors")
    assert result.data.get("data")[0]["status"] == "EDITING"
    assert result.data.get("data")[0]["user"] == user_2.id

    # (2) Change Task Status to CORRECTING_QUEUE by User_2 (corrector) -> OK
    new_task_status = Statuses.CORRECTING_QUEUE.value
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
        data={"status": new_task_status, "user": user_2.id},
        format="json",
    )

    assert result.data.get("success")
    assert not result.data.get("errors")
    assert result.data.get("data")[0]["status"] == "CORRECTING_QUEUE"
    assert result.data.get("data")[0]["user"] == user_2.id

    # (3) Change Task Status to CORRECTING by User_2 (corrector) -> OK
    new_task_status = Statuses.CORRECTING.value
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
        data={"status": new_task_status, "user": user_2.id},
        format="json",
    )

    assert result.data.get("success")
    assert not result.data.get("errors")
    assert result.data.get("data")[0]["status"] == "CORRECTING"
    assert result.data.get("data")[0]["user"] == user_2.id

    # (4) Change Task Status to TC_QUEUE by User_2 (corrector) -> OK
    new_task_status = Statuses.TC_QUEUE.value
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
        data={"status": new_task_status},
        format="json",
    )

    assert result.data.get("success")
    assert not result.data.get("errors")
    assert result.data.get("data")[0]["status"] == "TC_QUEUE"
    assert result.data.get("data")[0]["user"] == None

@pytest.mark.django_db
def test_changing_statuses_by_corrector_from_another_dep(api_client, super_user):
    """
    TestCase: User (corrector) from Dep_2 changes statuses to Editing when Task_department = 1 -> Error.
    """

    api_client.force_authenticate(super_user)

    # create user with department
    users_data = default_user_data(2,
                                   roles=[UserRoles.EDITOR.value, UserRoles.CORRECTOR.value])
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
        "user": user_1.id,
        "department": dep_1.id,
    }
    task = api_client.post(reverse("task-list"), data=task_data, format="json")

    # Login by user_2
    api_client.logout()
    api_client.force_authenticate(user_2)

    # (1) Change Task Status to Editing by User_2 (corrector) -> OK
    new_task_status = Statuses.EDITING.value
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
        data={"status": new_task_status, "user": user_2.id},
        format="json",
    )

    assert not result.data.get("success")
    assert result.data.get("errors")[0].get("attr") == "department"


@pytest.mark.django_db
def test_changing_statuses_by_verifier(api_client, super_user):

    """
    TestCase: User (verifier) changes statuses to Editing -> Error and Correcting -> Error.
    """

    api_client.force_authenticate(super_user)

    # create user with department
    users_data = default_user_data(2,
                                   roles=[UserRoles.EDITOR.value, UserRoles.VERIFIER.value])
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
        "user": user_1.id,
        "department": dep_1.id,
    }
    task = api_client.post(reverse("task-list"), data=task_data, format="json")

    # Login by user_2
    api_client.logout()
    api_client.force_authenticate(user_2)

    # (1) Change Task Status to Editing by User_2 (verifier) -> Error
    new_task_status = Statuses.EDITING.value
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
        data={"status": new_task_status},
        format="json",
    )

    assert not result.data.get("success")
    assert result.data.get("errors")[0].get("attr") == "status"


    # (2) Change Task Status to Correcting by User_2 (verifier) -> Error
    new_task_status = Statuses.CORRECTING.value
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
        data={"status": new_task_status},
        format="json",
    )

    assert not result.data.get("success")
    assert result.data.get("errors")[0].get("attr") == "status"


@pytest.mark.django_db
def test_changing_user_by_user(api_client, super_user):

    """
    TestCase: User (editor) changes user for Task to another user -> Error.
    """

    api_client.force_authenticate(super_user)

    # create user with department
    users_data = default_user_data(2,
                                   roles=[UserRoles.EDITOR.value, UserRoles.CORRECTOR.value])
    user_1, dep_1 = create_user_with_department(next(users_data), dep_name="Dep_1")
    user_2, dep_2 = create_user_with_department(next(users_data), dep_name="Dep_2")

    user_2.department = Department.objects.get(id=1)
    user_2.save()

    # create task
    task_data = {
        "name": "M-37-103-А",
        "scale": 50,
        "editing_time_estimate": 50,
        "correcting_time_estimate": 25,
        "tc_time_estimate": 15,
        "quarter": 1,
        "user": user_1.id,
        "department": dep_1.id,
    }
    task = api_client.post(reverse("task-list"), data=task_data, format="json")

    # (1) Change Task Status to Editing by Admin -> Success
    new_task_status = Statuses.EDITING.value
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
        data={"status": new_task_status, "user": user_1.id},
        format="json",
    )

    assert result.data.get("success")
    assert not result.data.get("errors")

    # Login by user_1
    api_client.logout()
    api_client.force_authenticate(user_1)

    # (2) Change task_user to user_2 by user_1 -> Error
    result = api_client.patch(
        reverse("task-detail", kwargs={"pk": task.data.get("data")[0].get("id")}),
        data={"user": user_2.id},
        format="json",
    )

    assert not result.data.get("success")
    assert result.data.get("errors")[0].get("attr") == "user"

