from __future__ import annotations

from typing import Optional, List

from django.contrib.auth import get_user_model

from . import graphql_input

__all__ = [
    "UserMutationType",
    "TagAnchorMutationType",
    "TagMutationType",
    "TutorialAnchorMutationType",
    "TutorialMutationType",
]

from ..models import (
    TagAnchor,
    UUIDMixin,
    StatusMixin,
    Tag,
    LangMixin,
    TutorialAnchor,
    Tutorial,
)


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


@graphql_input(
    TutorialAnchor, inject_mixin_fields=[UUIDMixin, StatusMixin], partial=True
)
class TutorialAnchorMutationType:
    url: str
    anchor_name: str
    tag_anchors: List[Optional[TagAnchorMutationType]]


@graphql_input(
    Tutorial, inject_mixin_fields=[UUIDMixin, StatusMixin, LangMixin], partial=True
)
class TutorialMutationType:
    tutorial_anchor: Optional[TutorialAnchorMutationType]
    authors: List[Optional[UserMutationType]]
    title: str
    abstract: str
    content_markdown: str
