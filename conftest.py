from typing import Generator, Any

import pytest

from rest_framework.test import APIClient

from api.models import User, Department, Task, TimeTracker


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
    return Department.objects.get_or_create(name=name)


def create_user_with_department(
    user_data, dep_name="DEFAULT_DEP"
) -> [dict, Department]:
    user = create_default_user(user_data)
    department = create_department(dep_name)
    user.department = department[0]
    user.save()
    return user, department[0]


def create_task(user: User = None, department: Department = None, name: str = "M-37-103-А") -> Task:
    data = {
        "name": name,
        "change_time_estimate": 50,
        "correct_time_estimate": 25,
        "otk_time_estimate": 15,
        "quarter": 1,
        "category": "some category",
        "user": user,
        "department": department,
    }
    return Task.objects.create(**data)


def create_time_tracker(task: Task, user: User) -> TimeTracker:
    data = {
        "task": task,
        "user": user,
    }
    return TimeTracker.objects.create(**data)
