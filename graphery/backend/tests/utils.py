from ..models import *

ADMIN_USERNAME = "admin"
USER_USERNAME = "user"
USER_PASSWORD = "password"


def add_admin_user(user_name: str = ADMIN_USERNAME) -> User:
    admin_user = User.objects.create_superuser(
        username=user_name, email="admin@admin.com", password=USER_PASSWORD
    )
    return admin_user


def add_normal_user(user_name: str = USER_USERNAME) -> User:
    normal_user = User.objects.create_user(
        username=user_name, email=f"{user_name}@user.com", password=USER_PASSWORD
    )
    return normal_user
