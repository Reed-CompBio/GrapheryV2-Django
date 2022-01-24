from __future__ import annotations

from typing import Iterable, Callable, Type
from uuid import uuid4

from django.db import models
from django.conf.global_settings import LANGUAGES

__all__ = [
    "UUIDMixin",
    "TimeDateMixin",
    "StatusMixin",
    "LangMixin",
    "Status",
    "UserRoles",
    "unique_with_lang",
]


class UUIDMixin(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)


class TimeDateMixin(models.Model):
    class Meta:
        abstract = True

    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)


class Status(models.TextChoices):
    DRAFT = "DRAFT", "draft"
    PUBLISHED = "PUBLISHED", "published"
    REVIEWING = "REVIEWING", "reviewing"
    PRIVATE = "PRIVATE", "private"
    TRASH = "TRASH", "trash"
    AUTOSAVE = "AUTOSAVE", "autosave"
    CLOSED = "CLOSED", "closed"


class StatusMixin(models.Model):
    class Meta:
        abstract = True

    _default_status = Status.DRAFT

    item_status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.DRAFT
    )


LangCode: models.TextChoices = models.TextChoices(
    value="LangCode", names=((x, (x, y)) for x, y in LANGUAGES)
)


class LangMixin(models.Model):
    class Meta:
        abstract = True

    lang_code = models.CharField(
        max_length=8,
        choices=LangCode.choices,
        default=LangCode.en,
        null=False,
        blank=False,
    )


def unique_with_lang(field_or_iterable: str | Iterable[str], cls_name: str) -> Callable:
    if isinstance(field_or_iterable, str):
        field_or_iterable = [field_or_iterable]

    def _helper(meta_cls: Type[models.Model]) -> Type[models.Model]:
        unique_cons = models.UniqueConstraint(
            fields=[*field_or_iterable, "lang_code"],
            name=f"unique_with_lang_{cls_name.lower()}",
        )

        if (cons := getattr(meta_cls, "constraints", None)) is None:
            cons = []

        setattr(
            meta_cls,
            "constraints",
            [*cons, unique_cons],
        )
        return meta_cls

    return _helper


def generate_group_name(tag: str | UserRoles) -> str:
    if isinstance(tag, str):
        tag = UserRoles(tag)
    elif not isinstance(tag, UserRoles):
        raise TypeError(
            "group name can only be generated by UserRoles instance or a role string"
        )

    return f"{tag.label} group"


class UserRoles(models.TextChoices):
    ADMINISTRATOR = "ADMINISTRATOR", "administrator"
    EDITOR = "EDITOR", "editor"
    AUTHOR = "AUTHOR", "author"
    TRANSLATOR = "TRANSLATOR", "translator"
    VISITOR = "VISITOR", "visitor"
    READER = "READER", "reader"

    @property
    def group_name(self) -> str:
        return generate_group_name(self)
