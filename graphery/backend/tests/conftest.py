import pytest
from django.contrib.sessions.middleware import SessionMiddleware

from ..baker_recipes import admin_user_recipe, user_recipe
from ..models import UserRoles


@pytest.fixture(scope="session")
def session_middleware():
    return SessionMiddleware()


@pytest.fixture(scope="function")
def admin_user(transactional_db):
    admin_user = admin_user_recipe.make()
    return admin_user


@pytest.fixture(scope="function")
def editor_user(transactional_db):
    editor_user = user_recipe.make(role=UserRoles.EDITOR)
    return editor_user


@pytest.fixture(scope="function")
def author_user(transactional_db):
    author_user = user_recipe.make(role=UserRoles.AUTHOR)
    return author_user


@pytest.fixture(scope="function")
def visitor_user(transactional_db):
    visitor_user = user_recipe.make(role=UserRoles.VISITOR)
    return visitor_user


@pytest.fixture(scope="function")
def reader_user(transactional_db):
    reader_user = user_recipe.make(role=UserRoles.READER)
    return reader_user


@pytest.fixture(scope="function")
def get_fixture(request, transactional_db):
    return request.getfixturevalue(request.param)
