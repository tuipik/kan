import pytest
from django.urls import reverse

from conftest import map_sheet_25k_name
from map_sheet.models import MapSheet


@pytest.mark.django_db
class TestMapSheet:

    @pytest.mark.parametrize("scale, map_sheet_name,", [
        (10, "map_sheet_10k_name"),
        (25, "map_sheet_25k_name"),
        (50, "map_sheet_50k_name"),
        (100, "map_sheet_100k_name"),
        (200, "map_sheet_200k_name"),
        (500, "map_sheet_500k_name"),
        (1000, "map_sheet_1kk_name"),
    ])
    def test_map_sheet(self, api_client, super_user, scale, map_sheet_name, request):

        api_client.force_authenticate(super_user)

        department_data = {"name": "test_department"}
        department = api_client.post(reverse("department-list"), data=department_data)
        department_id = department.data.get("data")[0].get("id")
        map_sheet_name = request.getfixturevalue(map_sheet_name)
        task_data = {
            # "name": "M-37-103-А-а",
            "name": map_sheet_name,
            "scale": scale,
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

        map_sheet = MapSheet.objects.get(name=task_data['name'])
        assert map_sheet
