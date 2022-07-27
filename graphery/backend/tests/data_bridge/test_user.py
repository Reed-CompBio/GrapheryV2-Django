from __future__ import annotations

import pytest
from django.contrib import auth
from model_bakery import baker

from ..utils import (
    async_make_django_context,
    async_save_session_in_request,
    make_request_with_user,
    bridge_test_helper,
)
from ...data_bridge import UserBridge, ValidationError
from ...models import User, UserRoles
from ...schema import schema
from ...types import UserMutationType

TEST_ADMIN_USERNAME = "admin"
TEST_PASSWORD = "password"


@pytest.fixture()
def user(transactional_db):
    user = baker.make(User)
    user.set_password(TEST_PASSWORD)
    user.save()
    return user


@pytest.mark.django_db
async def test_user(user, rf, session_middleware):
    mutation = """
        mutation LoginMutation($username:String!, $password: String!) {
            login(password: $password, username: $username) {
                id
            }
        }
    """

    request = rf.post("/graphql/sync", data=mutation, content_type="application/json")

    await async_save_session_in_request(request, session_middleware)

    result = await schema.execute(
        mutation,
        variable_values={
            "username": user.username,
            "password": TEST_PASSWORD,
        },
        context_value=await async_make_django_context(request),
    )

    assert result.errors is None
    assert result.data["login"]["id"] == str(user.id)


@pytest.mark.django_db
def test_user_data_bridge(user, rf):
    request = rf.post("/graphql/sync", data=None, content_type="application/json")
    request.user = user

    model_info = UserMutationType(
        id=user.id,
        username="new_username",
        email="new.email@gmail.org",
        displayed_name="new_displayed_name",
        in_mailing_list=True,
    )
    UserBridge.bridges_from_model_info(model_info, request=request)
    new_user = User.objects.get(id=user.id)

    assert new_user.username == model_info.username
    assert new_user.email == model_info.email
    assert new_user.displayed_name == model_info.displayed_name
    assert new_user.in_mailing_list == model_info.in_mailing_list


@pytest.mark.django_db
def test_user_data_bridge_changing_password(rf):
    user = baker.make(User)
    user.set_password(TEST_PASSWORD)
    user.save()

    model_info = UserMutationType(
        id=user.id,
        password=TEST_PASSWORD,
        new_password="new_password",
    )
    request = rf.post("/graphql/sync", data=None, content_type="application/json")
    request.user = user

    UserBridge.bridges_from_model_info(model_info, request=request)

    user = User.objects.get(id=user.id)

    auth_user = auth.authenticate(
        username=user.username, password=model_info.new_password
    )
    assert auth_user is not None
    assert auth_user.id == user.id

    request = rf.post("/graphql/sync", data=None, content_type="application/json")
    request.user = user

    with pytest.raises(ValidationError, match="Old password is incorrect"):
        UserBridge.bridges_from_model_info(model_info, request=request)

    user.delete()


@pytest.mark.django_db
def test_user_data_bridge_error_in_password_changing(user, rf):
    model_info = UserMutationType(
        id=user.id,
        new_password="new_password",
    )
    request = rf.post("/graphql/sync", data=None, content_type="application/json")
    request.user = user

    with pytest.raises(
        ValidationError, match="Old password is required to change to the new one"
    ):
        UserBridge.bridges_from_model_info(model_info, request=request)

    user = User.objects.get(id=user.id)

    auth_user = auth.authenticate(username=user.username, password=TEST_PASSWORD)
    assert auth_user is not None
    assert auth_user.id == user.id


@pytest.mark.django_db
def test_user_data_bridge_error_in_filling_unused_password(user, rf):
    model_info = UserMutationType(
        id=user.id,
        password=TEST_PASSWORD,
    )
    request = rf.post("/graphql/sync", data=None, content_type="application/json")
    request.user = user

    with pytest.raises(
        ValidationError,
        match="Submit new password to change the password, otherwise leave it empty",
    ):
        UserBridge.bridges_from_model_info(model_info, request=request)


def test_delete_user_by_admin(rf, user, admin_user):
    request = make_request_with_user(rf, admin_user)
    bridge_test_helper(
        UserBridge,
        UserMutationType(id=user.id),
        request=request,
        min_delete_user_role=UserRoles.ADMINISTRATOR,
        is_deleting=True,
    )


def test_delete_user_by_themself(rf, user):
    request = make_request_with_user(rf, user)
    bridge_test_helper(
        UserBridge,
        UserMutationType(id=user.id),
        request=request,
        is_deleting=True,
    )


def test_delete_user_by_others(rf, user, editor_user):
    request = make_request_with_user(rf, editor_user)
    bridge_test_helper(
        UserBridge,
        UserMutationType(id=user.id),
        request=request,
        is_deleting=True,
        delete_fail=True,
    )


@pytest.mark.skip(reason="not implemented")
@pytest.mark.django_db
async def test_user_mutation(user, rf, session_middleware):
    pass
