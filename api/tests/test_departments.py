import pytest
from rest_framework.reverse import reverse

from api.models import Status, BaseStatuses
from api.utils import fill_up_statuses


@pytest.mark.django_db
def test_CRUD_departments_ok(api_client, super_user):
    fill_up_statuses()

    api_client.force_authenticate(super_user)

    # test create
    statuses = Status.objects.filter(name__in=[BaseStatuses.WAITING.name, BaseStatuses.IN_PROGRESS.name])
    department_data = {"name": "test_department", "statuses": [statuses[0].id, statuses[1].id]}
    result = api_client.post(reverse("department-list"), data=department_data)

    assert result.data.get("success")
    assert not result.data.get("errors")
    assert result.data.get("data_len") == 1
    assert result.data.get("message") == "Created"

    all_departments = api_client.get(reverse("department-list"))

    assert all_departments.data.get("data_len") == 1
    assert all_departments.data.get("data")[0].get("name") == department_data.get(
        "name"
    )

    # test put
    department_obj = api_client.get(
        f"{reverse('account-list')}?name={department_data['name']}"
    )
    department_obj_id = department_obj.data.get("data")[0].get("id")
    new_department_name = {"name": "test_department"}

    result = api_client.put(
        reverse("department-detail", kwargs={"pk": department_obj_id}),
        data=new_department_name,
    )
    assert result.data.get("success")
    assert not result.data.get("errors")
    assert result.data.get("data_len") == 1
    assert result.data.get("message") == "Updated"

    department_updated = api_client.get(
        reverse("department-detail", kwargs={"pk": department_obj_id})
    )
    assert department_updated.data.get("data")[0].get(
        "name"
    ) == new_department_name.get("name")

    # test delete
    result = api_client.delete(
        reverse("department-detail", kwargs={"pk": department_obj_id})
    )
    assert result.data.get("success")
    assert not result.data.get("errors")
    assert result.data.get("data_len") == 0
    assert result.data.get("message") == "Deleted"

    all_users = api_client.get(reverse("department-list"))
    assert all_users.data.get("data_len") == 0


@pytest.mark.django_db
def test_add_department_head(api_client, super_user):
    fill_up_statuses()

    api_client.force_authenticate(super_user)

    statuses = Status.objects.filter(name__in=[BaseStatuses.WAITING.name, BaseStatuses.IN_PROGRESS.name])
    department_data = {"name": "test_department", "statuses": [statuses[0].id, statuses[1].id]}
    department = api_client.post(reverse("department-list"), data=department_data)
    department_id = department.data.get("data")[0].get("id")

    updated_user = api_client.patch(
        reverse("account-detail", kwargs={"pk": super_user.id}),
        data={"department": department_id},
    )
    assert updated_user.data.get("success")

    updated_department = api_client.patch(
        reverse("department-detail", kwargs={"pk": department_id}),
        data={"head": super_user.id},
    )
    assert updated_department.data.get("success")
    assert updated_department.data.get("data")[0].get("head") == super_user.id

    new_department = api_client.post(
        reverse("department-list"), data={"name": "new_test_department", "statuses": [statuses[0].id, statuses[1].id]}
    )
    assert new_department.data.get("success")
    new_department_id = new_department.data.get("data")[0].get("id")
    updated_department = api_client.patch(
        reverse("department-detail", kwargs={"pk": new_department_id}),
        data={"head": super_user.id},
    )

    assert not updated_department.data.get("success")
    assert updated_department.status_code == 400
    assert updated_department.data.get("errors")[0].get("code") == "invalid"
    assert updated_department.data.get("errors")[0].get("attr") == "head"
