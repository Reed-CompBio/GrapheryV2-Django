import strawberry
from strawberry.django import auto
from django.contrib.auth import get_user_model
from .utils import graphql_type

__all__ = ["UserType", "UserInput"]


@graphql_type(get_user_model())
class UserType:
    username: auto
    email: auto
    displayed_name: auto
    role: auto
    is_staff: auto


@strawberry.django.input(get_user_model())
class UserInput:
    username: auto
    password: auto
