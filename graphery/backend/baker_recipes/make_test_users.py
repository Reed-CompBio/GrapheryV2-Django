from __future__ import annotations

from ..models import User, UserRoles


def make_admin_user():
    user = User.objects.create_user(
        username="test_admin_user",
        password="test_admin_user",
        email="test_admin_user@admin.net",
        role=UserRoles.ADMINISTRATOR,
    )
    return user
