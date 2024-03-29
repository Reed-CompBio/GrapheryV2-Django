# Generated by Django 3.2.10 on 2022-01-23 04:26

import backend.models.user
import django.contrib.auth.validators
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        help_text="Required Field. 150 characters or fewer. Letters, digits and @/./+/-/_ only",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "displayed_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="displayed name"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=254, unique=True, verbose_name="email address"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "verification_key",
                    models.CharField(
                        default=backend.models.user._generate_verification_key,
                        help_text="Designates whether this user is activated or not",
                        max_length=48,
                        null=True,
                        verbose_name="is activated",
                    ),
                ),
                (
                    "in_mailing_list",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user has opted in the mailing list",
                        verbose_name="in mailing list",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="Indicate when this user is created.",
                        verbose_name="date joined",
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("ADMINISTRATOR", "administrator"),
                            ("EDITOR", "editor"),
                            ("AUTHOR", "author"),
                            ("TRANSLATOR", "translator"),
                            ("VISITOR", "visitor"),
                            ("READER", "reader"),
                        ],
                        default="READER",
                        max_length=20,
                        verbose_name="user role",
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.Group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.Permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            managers=[
                ("objects", backend.models.user.CustomUserManager()),
            ],
        ),
    ]
