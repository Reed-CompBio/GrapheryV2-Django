from __future__ import annotations

import pytest
from model_bakery import baker

from .utils import async_make_django_context, async_save_session_in_request
from ..data_bridge import UserBridge
from ..models import User
from ..schema import schema
from ..types import UserMutationType

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
    bridge = UserBridge(user.id)
    request = rf.post("/graphql/sync", data=None, content_type="application/json")
    request.user = user

    model_info = UserMutationType(
        id=user.id,
        username="new_username",
        email="new.email@gmail.org",
        displayed_name="new_displayed_name",
        in_mailing_list=True,
    )
    bridge.bridges_from_model_info(model_info, request=request)
    new_user = User.objects.get(id=user.id)

    assert new_user.username == model_info.username
    assert new_user.email == model_info.email
    assert new_user.displayed_name == model_info.displayed_name
    assert new_user.in_mailing_list == model_info.in_mailing_list


@pytest.mark.django_db
async def test_user_mutation(user, rf, session_middleware):
    pass
