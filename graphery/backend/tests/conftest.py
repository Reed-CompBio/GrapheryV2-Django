import pytest
from django.contrib.sessions.middleware import SessionMiddleware


@pytest.fixture(scope="session")
def session_middleware():
    return SessionMiddleware()
