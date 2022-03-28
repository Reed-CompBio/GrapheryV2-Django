from __future__ import annotations

import strawberry

from django.contrib.auth import get_user_model

from . import graphql_input

__all__ = ["UserMutationType"]


@graphql_input(get_user_model(), inject_mixin_fields=False, partial=True)
class UserMutationType:
    id: strawberry.ID
    username: str
    password: str
    new_password: str
    email: str
    displayed_name: str
    in_mailing_list: bool
