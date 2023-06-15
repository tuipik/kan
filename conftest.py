from typing import Generator, Any

import pytest

from rest_framework.test import APIClient

from api.models import User


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
