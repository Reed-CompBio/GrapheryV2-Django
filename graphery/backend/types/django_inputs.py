from __future__ import annotations

from django.contrib.auth import get_user_model
from strawberry.django import auto

from . import graphql_input


@graphql_input(get_user_model())
class UserLoginType:
    username: auto
    password: auto
