import strawberry
from strawberry.django import auto
from django.contrib.auth import get_user_model


__all__ = ["User", "UserInput"]


@strawberry.django.type(get_user_model())
class User:
    username: auto
    email: auto
    displayed_name: auto
    role: auto
    is_staff: auto


@strawberry.django.input(get_user_model())
class UserInput:
    username: auto
    password: auto
