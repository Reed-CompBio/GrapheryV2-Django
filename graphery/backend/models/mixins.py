from __future__ import annotations

import uuid
from datetime import datetime
from typing import Iterable, Callable, Type, Mapping
from uuid import uuid4

from django.db import models
from django.conf.global_settings import LANGUAGES

__all__ = [
    "MixinBase",
    "UUIDMixin",
    "TimeDateMixin",
    "StatusMixin",
    "LangMixin",
    "RankMixin",
    "Status",
    "LangCode",
    "UserRoles",
    "GraphOrder",
    "unique_with_lang",
]


class MixinBase:
    _graphql_types: Mapping[str, Type] = {}
    _auto_require: bool = True

    @classmethod
    def inject_graphql_types(cls, wrapped_cls) -> None:
        if not cls._auto_require:
            return

        if not all(
            isinstance(attr, str) and isinstance(attr_type, type)
            for attr, attr_type in cls._graphql_types.items()
        ):
            raise TypeError(
                f"arguments must be a mapping of str:type, {cls} got {cls._graphql_types}"
            )

        annotated_to = getattr(wrapped_cls, "__annotations__", None)
        if annotated_to is None:
            raise TypeError(f"{wrapped_cls} must have annotations")

        annotated_to.update(cls._graphql_types)


class UUIDMixin(models.Model, MixinBase):
    _graphql_types = {"id": uuid.UUID}

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class TimeDateMixin(models.Model, MixinBase):
    _graphql_types = {"created_time": datetime, "modified_time": datetime}

    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Status(models.TextChoices):
    DRAFT = "DRAFT", "draft"
    PUBLISHED = "PUBLISHED", "published"
    REVIEWING = "REVIEWING", "reviewing"
    PRIVATE = "PRIVATE", "private"
    TRASH = "TRASH", "trash"
    AUTOSAVE = "AUTOSAVE", "autosave"
    CLOSED = "CLOSED", "closed"


class StatusMixin(models.Model, MixinBase):
    _default_status = Status.DRAFT
    _graphql_types = {"item_status": str}

    item_status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.DRAFT
    )

    class Meta:
        abstract = True


# noinspection PyArgumentList
LangCode = models.TextChoices(
    value="LangCode",
    names=((x.upper(), (x.upper(), y)) for x, y in LANGUAGES),
)


class LangMixin(models.Model, MixinBase):
    _graphql_types = {"lang_code": str}

    lang_code = models.CharField(
        max_length=8,
        choices=LangCode.choices,
        default=LangCode.EN,
        null=False,
        blank=False,
    )

    class Meta:
        abstract = True


class RankMixin(models.Model, MixinBase):
    _graphql_types = {"rank": str}

    rank = models.CharField(max_length=3, null=False, blank=False, unique=True)

    class Meta:
        abstract = True


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


def generate_group_name(tag: int | UserRoles) -> str:
    if isinstance(tag, int):
        tag = UserRoles(tag)
    elif not isinstance(tag, UserRoles):
        raise TypeError(
            "group name can only be generated by UserRoles instance or a role string"
        )

    return f"{tag.label} group"


class UserRoles(models.IntegerChoices):
    ADMINISTRATOR = 5, "administrator"
    EDITOR = 4, "editor"
    AUTHOR = 3, "author"
    TRANSLATOR = 2, "translator"
    VISITOR = 1, "visitor"
    READER = 0, "reader"

    @property
    def group_name(self) -> str:
        return generate_group_name(self)


class GraphOrder(models.IntegerChoices):
    HIGH = 100, "high"
    MEDIUM = 60, "medium"
    LOW = 20, "low"
