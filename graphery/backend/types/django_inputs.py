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
    "GraphAnchorMutationType",
    "OrderedGraphAnchorMutationType",
    "GraphMutationType",
    "GraphDescriptionMutationType",
]

from ..models import (
    TagAnchor,
    UUIDMixin,
    StatusMixin,
    Tag,
    LangMixin,
    TutorialAnchor,
    Tutorial,
    GraphAnchor,
    OrderedGraphAnchor,
    Graph,
    GraphDescription,
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


@graphql_input(GraphAnchor, inject_mixin_fields=[UUIDMixin, StatusMixin], partial=True)
class GraphAnchorMutationType:
    url: str
    anchor_name: str
    tag_anchors: List[Optional[TagAnchorMutationType]]
    default_order: int
    tutorial_anchor: List[Optional[TutorialAnchorMutationType]]


@graphql_input(OrderedGraphAnchor, inject_mixin_fields=[UUIDMixin], partial=True)
class OrderedGraphAnchorMutationType:
    graph_anchor: Optional[GraphAnchorMutationType]
    tutorial_anchor: Optional[TutorialAnchorMutationType]
    order: int


@graphql_input(Graph, inject_mixin_fields=[UUIDMixin, StatusMixin], partial=True)
class GraphMutationType:
    graph_anchors: Optional[GraphAnchor]
    graph_json: str
    makers: List[Optional[UserMutationType]]


@graphql_input(
    GraphDescription,
    inject_mixin_fields=[UUIDMixin, StatusMixin, LangMixin],
    partial=True,
)
class GraphDescriptionMutationType:
    graph_anchor: Optional[GraphAnchorMutationType]
    authors: List[Optional[UserMutationType]]
    title: str
    description_markdown: str
