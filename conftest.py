from typing import Generator, Any

import pytest

from rest_framework.test import APIClient

from api.models import User, Department, Task, TimeTracker, Status


@pytest.fixture(scope="function")
def api_client() -> APIClient:
    yield APIClient()


@pytest.fixture(scope="function")
def super_user() -> User:
    data = {
        "username": "test_superuser",
        "first_name": "test_f_name",
        "last_name": "test_l_name",
        "password": "test_pass",
    }
    return User.objects.create_superuser(**data)


def default_user_data(num) -> Generator[dict[str, str], Any, None]:
    counter = 0
    while True:
        counter += 1
        if counter > num:
            raise StopIteration()
        yield {
            "username": f"default_user_{counter}",
            "first_name": f"default_f_name_{counter}",
            "last_name": f"default_l_name_{counter}",
            "password": "default_pass",
            "password2": "default_pass",
            "department": "",
        }


def create_default_user(user_data) -> User:
    del user_data["department"]
    del user_data["password2"]
    return User.objects.create(**user_data)


def create_department(name="DEFAULT_DEP") -> [Department, bool]:
    dep, created = Department.objects.get_or_create(name=name)
    dep.statuses.set([1, 2])
    dep.save()
    return dep


def create_user_with_department(
    user_data, dep_name="DEFAULT_DEP"
) -> [dict, Department]:
    user = create_default_user(user_data)
    department = create_department(dep_name)
    user.department = department
    user.save()
    return user, department


def create_task(
    user: User = None, department: Department = None, name: str = "M-37-103-А"
) -> Task:
    status = Status.objects.all()
    data = {
        "name": name,
        "status": status[0],
        "change_time_estimate": 50,
        "correct_time_estimate": 25,
        "vtk_time_estimate": 15,
        "quarter": 1,
        "category": 3,
        "user": user,
        "department": department,
        "primary_department": department,
    }
    task = Task.objects.create(**data)
    time_tracker_data = {
        "task": task,
        "user": user,
        "task_status": status[0],
    }
    TimeTracker.objects.create(**time_tracker_data)
    return task


def create_time_tracker(task: Task, user: User) -> TimeTracker:
    data = {
        "task": task,
        "user": user,
        "task_status": 1
    }
    return TimeTracker.objects.create(**data)
