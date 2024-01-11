from typing import Generator, Any

import pytest

from rest_framework.test import APIClient

from api.CONSTANTS import ROWS_CHOICES, COLUMNS_CHOICES, TRAPEZE_500K_AND_50K_CHOICES, ROMAN_NUMBERS, \
    TRAPEZE_100K_CHOICES, TRAPEZE_25K_CHOICES, TRAPEZE_10K_CHOICES
from api.models import User, Department, Task, TimeTracker, Statuses, Comment
from map_sheet.models import MapSheet


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


def default_user_data(num, roles:list) -> Generator[dict[str, str], Any, None]:
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
            "role": roles[counter-1]
        }


def create_default_user(user_data) -> User:
    del user_data["department"]
    del user_data["password2"]
    return User.objects.create(**user_data)


def create_department(name="DEFAULT_DEP") -> [Department, bool]:
    dep, created = Department.objects.get_or_create(name=name)
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
    data = {
        "name": name,
        "status": Statuses.EDITING_QUEUE.value,
        "editing_time_estimate": 50,
        "correcting_time_estimate": 25,
        "tc_time_estimate": 15,
        "quarter": 1,
        "category": 3,
        "user": user,
        "department": department,
    }
    task = Task.objects.create(**data)
    time_tracker_data = {
        "task": task,
        "user": user,
        "task_status": Statuses.EDITING_QUEUE.value,
        "task_department": task.department,
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


# MapSheet
@pytest.fixture(scope="session")
def column_name():
    yield COLUMNS_CHOICES[0]

@pytest.fixture(scope="session")
def row_name():
    yield ROWS_CHOICES[0]

@pytest.fixture(scope="session")
def trapeze_500k():
    yield TRAPEZE_500K_AND_50K_CHOICES[0]

@pytest.fixture(scope="session")
def trapeze_200k():
    yield ROMAN_NUMBERS[0]
@pytest.fixture(scope="session")
def trapeze_100k():
    yield TRAPEZE_100K_CHOICES[0]

@pytest.fixture(scope="session")
def trapeze_50k():
    yield TRAPEZE_500K_AND_50K_CHOICES[0]

@pytest.fixture(scope="session")
def trapeze_25k():
    yield TRAPEZE_25K_CHOICES[0]

@pytest.fixture(scope="session")
def trapeze_10k():
    yield TRAPEZE_10K_CHOICES[0]

@pytest.fixture(scope="session")
def map_sheet_1kk_name(row_name, column_name):
    yield f"{row_name}-{column_name}"

@pytest.fixture(scope="session")
def map_sheet_500k_name(map_sheet_1kk_name, trapeze_500k):
    yield f"{map_sheet_1kk_name}-{trapeze_500k}"

@pytest.fixture(scope="session")
def map_sheet_200k_name(map_sheet_1kk_name, trapeze_200k):
    yield f"{map_sheet_1kk_name}-{trapeze_200k}"

@pytest.fixture(scope="session")
def map_sheet_100k_name(map_sheet_1kk_name, trapeze_100k):
    yield f"{map_sheet_1kk_name}-{trapeze_100k}"

@pytest.fixture(scope="session")
def map_sheet_50k_name(map_sheet_100k_name, trapeze_50k):
    yield f"{map_sheet_100k_name}-{trapeze_50k}"

@pytest.fixture(scope="session")
def map_sheet_25k_name(map_sheet_50k_name, trapeze_25k):
    yield f"{map_sheet_50k_name}-{trapeze_25k}"

@pytest.fixture(scope="session")
def map_sheet_10k_name(map_sheet_25k_name, trapeze_10k):
    yield f"{map_sheet_25k_name}-{trapeze_10k}"


# Department
@pytest.fixture
def gis_department():
    department = Department(name="GIS")
    department.save()
    yield department

# Auto use
@pytest.fixture(autouse=True)
def clear_table():
    models = (User, Task, Department, TimeTracker, Comment, MapSheet,)
    for model in models:
        model.objects.all().delete()
    yield
    for model in models:
        model.objects.all().delete()
