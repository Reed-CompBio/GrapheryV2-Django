import warnings

from django.apps import apps
from django.contrib import auth
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager, PermissionsMixin, Group
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string

from .mixins import UUIDMixin, UserRoles


class CustomUserManager(UserManager):
    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError("The given username must be set")
        email = self.normalize_email(email)
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        global_user_model_cls = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        username = global_user_model_cls.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, email, password, **extra_fields)

    def with_perm(
        self, perm, is_active=True, include_superusers=True, backend=None, obj=None
    ):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    "You have multiple authentication backends configured and "
                    "therefore must provide the `backend` argument."
                )
        elif not isinstance(backend, str):
            raise TypeError(
                "backend must be a dotted import path string (got %r)." % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, "with_perm"):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


_VERIFICATION_KEY_LENGTH = 48


def _generate_verification_key() -> str | None:
    if settings.USER_IS_VERIFIED_DEFAULT:
        return None
    else:
        return get_random_string(_VERIFICATION_KEY_LENGTH)


class User(UUIDMixin, AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        "username",
        max_length=150,
        unique=True,
        help_text=(
            "Required Field. 150 characters or fewer. Letters, digits and @/./+/-/_ only"
        ),
        validators=[username_validator],
    )
    displayed_name = models.CharField("displayed name", max_length=150, blank=True)
    email = models.EmailField("email address", unique=True)
    is_staff = models.BooleanField(
        "staff status",
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )
    is_active = models.BooleanField(
        "active",
        default=True,
        help_text="Designates whether this user should be treated as active. "
        "Unselect this instead of deleting accounts.",
    )
    verification_key = models.CharField(
        "is activated",
        max_length=_VERIFICATION_KEY_LENGTH,
        default=_generate_verification_key,
        help_text="Designates whether this user is activated or not",
        null=False,
        blank=True,
    )
    in_mailing_list = models.BooleanField(
        "in mailing list",
        default=settings.USER_EMAIL_OPT_IN_DEFAULT,
        help_text="Designates whether this user has opted in the mailing list",
    )
    date_joined = models.DateTimeField(
        "date joined",
        auto_now_add=True,
        help_text="Indicate when this user is created.",
    )
    role = models.CharField(
        "user role", max_length=20, choices=UserRoles.choices, default=UserRoles.READER
    )

    objects = CustomUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"

    REQUIRED_FIELDS = ("email",)

    @property
    def is_verified(self) -> bool:
        return not bool(self.verification_key)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Email this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


@receiver(post_save)
def _modify_role(instance, **_):
    role = instance.role
    if not isinstance(role, UserRoles):
        raise TypeError(f"{role} is not valid user role.")

    try:
        instance.groups.clear()
    except Exception as e:
        warnings.warn(f"Exception occurs when clearing user groups: {e}")

    try:
        instance.groups.add(Group.objects.get(name=role.group_name))
    except Group.DoesNotExist:
        warnings.warn(f"{role.group_name} does not exist")
    except Exception as e:
        warnings.warn(f"Exception occurs when add user group: {e}")
