from __future__ import annotations

import pytest
from asgiref.sync import sync_to_async
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponse
from model_bakery import baker
from strawberry.django.context import StrawberryDjangoContext

from ..models import User
from ..schema import schema

TEST_ADMIN_USERNAME = "admin"
TEST_PASSWORD = "password"


@pytest.fixture()
def user(transactional_db):
    user = baker.make(User)
    user.set_password(TEST_PASSWORD)
    user.save()
    return user


@pytest.fixture()
def session_middleware():
    return SessionMiddleware()


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

    session_middleware.process_request(request)
    sync_to_async(request.session.save)()

    result = await schema.execute(
        mutation,
        variable_values={
            "username": user.username,
            "password": TEST_PASSWORD,
        },
        context_value=StrawberryDjangoContext(request, HttpResponse()),
    )

    assert result.errors is None
    assert result.data["login"]["id"] == str(user.id)
