from __future__ import annotations

from typing import Optional

from django.contrib.auth import get_user_model

from . import graphql_input

__all__ = ["UserMutationType"]

from ..models import TagAnchor, UUIDMixin, StatusMixin, Tag, LangMixin


@graphql_input(get_user_model(), inject_mixin_fields=[UUIDMixin], partial=True)
class UserMutationType:
    username: str
    password: str
    new_password: str
    email: str
    displayed_name: str
    in_mailing_list: bool


@graphql_input(TagAnchor, inject_mixin_fields=[UUIDMixin, StatusMixin], partial=True)
class TagAnchorMutationType:
    anchor_name: str


@graphql_input(
    Tag, inject_mixin_fields=[UUIDMixin, StatusMixin, LangMixin], partial=True
)
class TagMutationType:
    name: str
    tag_anchor: Optional[TagAnchorMutationType]
    description: str
