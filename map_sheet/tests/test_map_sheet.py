from unittest import mock

import pytest

from api.serializers import TaskSerializer
from map_sheet.models import MapSheet


@pytest.mark.django_db
class TestMapSheet:

    @pytest.mark.parametrize(
        "scale, map_sheet_name, trapeze10k, trapeze25k, trapeze50k, trapeze100k, trapeze200k, trapeze500k, trapeze1000k",
        [
            (10, "map_sheet_10k_name", "trapeze_10k", "trapeze_25k","trapeze_50k", "trapeze_100k", None, None, None),
            (25, "map_sheet_25k_name", None, "trapeze_25k", "trapeze_50k", "trapeze_100k", None, None, None),
            (50, "map_sheet_50k_name", None, None, "trapeze_50k", "trapeze_100k", None, None, None),
            (100, "map_sheet_100k_name", None, None, None, "trapeze_100k", None, None, None),
            (200, "map_sheet_200k_name", None, None, None, None, "trapeze_200k", None, None),
            (500, "map_sheet_500k_name", None, None, None, None, None, "trapeze_500k", None),
            (1000, "map_sheet_1kk_name", None, None, None, None, None, None, None),
        ]
    )
    @mock.patch("api.serializers.TaskSerializer._create_log_data")
    def test_map_sheet_create(
            self, _create_log_data_mock, api_client, super_user, scale, map_sheet_name, trapeze10k, trapeze25k,
            trapeze50k, trapeze100k, trapeze200k, trapeze500k, trapeze1000k, row_name, column_name, request,
            map_sheet_50k_name, trapeze_100k, trapeze_50k, trapeze_25k, trapeze_10k, gis_department,
    ):
        """
        Creates task for each scale and check that for each task corresponding MapSheet created

        """
        department_id = gis_department.id
        map_sheet_name = request.getfixturevalue(map_sheet_name)
        task_data = {
            "name": map_sheet_name,
            "scale": scale,
            "editing_time_estimate": 50,
            "correcting_time_estimate": 25,
            "tc_time_estimate": 15,
            "quarter": 1,
            "category": 3,
            "department": department_id,
        }

        serializer = TaskSerializer(data=task_data)
        assert serializer.is_valid()
        _create_log_data_mock.return_value = {"log_user": super_user, "log_text": "", "is_log": False}
        task = serializer.save()

        map_sheet = MapSheet.objects.get(name=task_data['name'])

        assert task.map_sheet.id == map_sheet.id
        assert map_sheet.name == map_sheet_name
        assert map_sheet.scale == scale
        assert map_sheet.row == row_name
        assert map_sheet.column == int(column_name)

        assert str(map_sheet.trapeze_10k) == str(trapeze10k and request.getfixturevalue(trapeze10k))
        assert str(map_sheet.trapeze_25k) == str(trapeze25k and request.getfixturevalue(trapeze25k))
        assert str(map_sheet.trapeze_50k) == str(trapeze50k and request.getfixturevalue(trapeze50k))
        assert str(map_sheet.trapeze_100k) == str(trapeze100k and request.getfixturevalue(trapeze100k))
        assert str(map_sheet.trapeze_200k) == str(trapeze200k and request.getfixturevalue(trapeze200k))
        assert str(map_sheet.trapeze_500k) == str(trapeze500k and request.getfixturevalue(trapeze500k))

    @pytest.mark.parametrize(
        "scale, map_sheet_name, trapeze10k, trapeze25k, trapeze50k, trapeze100k, trapeze200k, trapeze500k, trapeze1000k",
        [
            (10, "map_sheet_10k_name", "trapeze_10k", "trapeze_25k","trapeze_50k", "trapeze_100k", None, None, None),
            (25, "map_sheet_25k_name", None, "trapeze_25k", "trapeze_50k", "trapeze_100k", None, None, None),
            (100, "map_sheet_100k_name", None, None, None, "trapeze_100k", None, None, None),
            (200, "map_sheet_200k_name", None, None, None, None, "trapeze_200k", None, None),
            (500, "map_sheet_500k_name", None, None, None, None, None, "trapeze_500k", None),
            (1000, "map_sheet_1kk_name", None, None, None, None, None, None, None),
        ]
    )
    @mock.patch("api.serializers.TaskSerializer._create_log_data")
    def test_map_sheet_update(
            self, _create_log_data_mock, api_client, super_user, scale, map_sheet_name, trapeze10k, trapeze25k,
            trapeze50k, trapeze100k, trapeze200k, trapeze500k, trapeze1000k, row_name, column_name, request,
            map_sheet_50k_name, trapeze_100k, trapeze_50k, trapeze_25k, trapeze_10k, gis_department,
    ):
        """
        Creates task with 50k scale, then it updated by data for each scale (except 50k) and check, that MapSheet was
        updated by corresponding data

        """
        map_sheet_name = request.getfixturevalue(map_sheet_name)
        task_data = {
            "name": map_sheet_50k_name,
            "scale": 50,
            "editing_time_estimate": 50,
            "correcting_time_estimate": 25,
            "tc_time_estimate": 15,
            "quarter": 1,
            "category": 3,
            "department": gis_department.id,
        }

        serializer = TaskSerializer(data=task_data)
        assert serializer.is_valid()
        _create_log_data_mock.return_value = {"log_user": super_user, "log_text": "", "is_log": False}
        task = serializer.save()
        initial_map_sheet_name = task.map_sheet.name
        initial_map_sheet_id = task.map_sheet.id

        new_task_data = {"name": map_sheet_name, "scale": scale, "department": gis_department.id}
        serializer = TaskSerializer(data=new_task_data, instance=task)
        assert serializer.is_valid()
        updated_task = serializer.save()

        assert updated_task.name == map_sheet_name

        updated_map_sheet = updated_task.map_sheet
        db_map_sheet = MapSheet.objects.get(name=map_sheet_name)
        assert db_map_sheet.id == updated_map_sheet.id == initial_map_sheet_id  # Ensure that MapSheet remains the same

        new_map_sheet_name = updated_map_sheet.name
        assert initial_map_sheet_name != new_map_sheet_name

        assert str(updated_map_sheet.trapeze_10k) == str(trapeze10k and request.getfixturevalue(trapeze10k))
        assert str(updated_map_sheet.trapeze_25k) == str(trapeze25k and request.getfixturevalue(trapeze25k))
        assert str(updated_map_sheet.trapeze_50k) == str(trapeze50k and request.getfixturevalue(trapeze50k))
        assert str(updated_map_sheet.trapeze_100k) == str(trapeze100k and request.getfixturevalue(trapeze100k))
        assert str(updated_map_sheet.trapeze_200k) == str(trapeze200k and request.getfixturevalue(trapeze200k))
        assert str(updated_map_sheet.trapeze_500k) == str(trapeze500k and request.getfixturevalue(trapeze500k))
