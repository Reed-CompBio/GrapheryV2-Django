from __future__ import print_function

from django.contrib.auth.hashers import make_password
from model_bakery import seq
from model_bakery.recipe import Recipe

from ..models import User, UserRoles

ADMIN_PREFIX = "admin"
USER_PREFIX = "user"
USER_PASSWORD = "password"
EMAIL_SUFFIX = "@example.com"

__all__ = [
    "ADMIN_PREFIX",
    "USER_PREFIX",
    "USER_PASSWORD",
    "EMAIL_SUFFIX",
    "admin_user_recipe",
    "user_recipe",
]

admin_user_recipe = Recipe(
    User,
    username=seq(ADMIN_PREFIX),
    password=make_password(USER_PASSWORD),
    email=seq(ADMIN_PREFIX, suffix=EMAIL_SUFFIX),
    is_superuser=True,
    is_staff=True,
    role=UserRoles.ADMINISTRATOR,
)

user_recipe = Recipe(
    User,
    username=seq(USER_PREFIX),
    password=make_password(USER_PASSWORD),
    email=seq(USER_PREFIX, suffix=EMAIL_SUFFIX),
    is_superuser=False,
    is_staff=False,
)
