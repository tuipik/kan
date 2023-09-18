import pytest
from rest_framework.reverse import reverse

from helpers import fill_up_statuses
from conftest import default_user_data, create_user_with_department


@pytest.mark.django_db
def test_CRUD_accounts_ok(api_client, super_user):
    fill_up_statuses()

    default_user_num = 2
    all_users_num = default_user_num + 1

    api_client.force_authenticate(super_user)

    # test create
    users_data = default_user_data(default_user_num)
    user_1 = next(users_data)
    user_2 = next(users_data)
    api_client.post(reverse("account-list"), data=user_1)
    api_client.post(reverse("account-list"), data=user_2)

    all_users = api_client.get(reverse("account-list"))

    assert all_users.data.get("data_len") == all_users_num
    assert all_users.data.get("data")[0].get("username") == super_user.username
    assert all_users.data.get("data")[0].get("is_admin") == super_user.is_admin
    assert all_users.data.get("data")[1].get("username") == user_1.get("username")
    assert not all_users.data.get("data")[1].get("is_admin")
    assert all_users.data.get("data")[2].get("username") == user_2.get("username")
    assert not all_users.data.get("data")[2].get("is_admin")

    # test put
    user_1_obj = api_client.get(
        f"{reverse('account-list')}?username={user_1['username']}"
    )
    user_1_obj_id = user_1_obj.data.get("data")[0].get("id")
    del user_1["password"]
    del user_1["password2"]
    new_username = "new_username"
    user_1["username"] = new_username

    result = api_client.put(
        reverse("account-detail", kwargs={"pk": user_1_obj_id}), data=user_1
    )
    assert result.data.get("success")
    assert not result.data.get("errors")
    assert result.data.get("data_len") == 1
    assert result.data.get("message") == "Updated"

    user_1_updated = api_client.get(
        reverse("account-detail", kwargs={"pk": user_1_obj_id})
    )
    assert user_1_updated.data.get("data")[0].get("username") == new_username

    # test patch
    new_first_name = {"first_name": "new_first_name"}

    result = api_client.patch(
        reverse("account-detail", kwargs={"pk": user_1_obj_id}), data=new_first_name
    )
    assert result.data.get("success")
    assert not result.data.get("errors")
    assert result.data.get("data_len") == 1
    assert result.data.get("message") == "Updated"

    user_1_patched = api_client.get(
        reverse("account-detail", kwargs={"pk": user_1_obj_id})
    )
    assert user_1_patched.data.get("data")[0].get("username") == new_username
    assert user_1_patched.data.get("data")[0].get("first_name") == new_first_name.get(
        "first_name"
    )

    # test delete
    result = api_client.delete(reverse("account-detail", kwargs={"pk": user_1_obj_id}))
    assert result.data.get("success")
    assert not result.data.get("errors")
    assert result.data.get("data_len") == 0
    assert result.data.get("message") == "Deleted"

    all_users = api_client.get(reverse("account-list"))
    assert all_users.data.get("data_len") == all_users_num - 1


@pytest.mark.django_db
def test_not_admin(api_client):
    fill_up_statuses()

    users_data = default_user_data(2)
    user_1_data = next(users_data)
    user, department = create_user_with_department(user_1_data)

    api_client.force_authenticate(user)
    all_users_resp = api_client.get(reverse("account-list"))
    user_1_resp = api_client.post(reverse("account-list"), data=next(users_data))

    assert all_users_resp.status_code == 200
    assert user_1_resp.status_code == 403
    assert user_1_resp.data.get("errors")[0].get("code") == "permission_denied"


@pytest.mark.django_db
def test_not_authenticated(api_client):
    fill_up_statuses()

    users_data = default_user_data(2)
    all_users_resp = api_client.get(reverse("account-list"))
    user_1_resp = api_client.post(reverse("account-list"), data=next(users_data))

    assert all_users_resp.status_code == 401
    assert all_users_resp.data.get("errors")[0].get("code") == "not_authenticated"
    assert user_1_resp.status_code == 401
    assert user_1_resp.data.get("errors")[0].get("code") == "not_authenticated"
