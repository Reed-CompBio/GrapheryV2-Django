from __future__ import annotations

import enum
from typing import Optional, List

import strawberry
from django.contrib.auth import get_user_model

from . import graphql_input

from ..models import (
    TagAnchor,
    UUIDMixin,
    StatusMixin,
    Tag,
    LangMixin,
    TutorialAnchor,
    Tutorial,
    GraphAnchor,
    Graph,
    GraphDescription,
    Code,
    ExecutionResult,
)


__all__ = [
    "UserMutationType",
    "TagAnchorMutationType",
    "TagMutationType",
    "TutorialAnchorMutationType",
    "TutorialMutationType",
    "GraphAnchorMutationType",
    "OrderedTutorialAnchorBindingType",
    "OrderedGraphAnchorBindingType",
    "GraphMutationType",
    "GraphDescriptionMutationType",
    "CodeMutationType",
    "ExecutionResultMutationType",
    "OperationType",
]


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
    # related fields
    graph_anchors: List[Optional[OrderedGraphAnchorBindingType]]


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
    tutorial_anchors: List[Optional[OrderedTutorialAnchorBindingType]]


@strawberry.input
class OrderedTutorialAnchorBindingType:
    tutorial_anchor: TutorialAnchorMutationType
    order: Optional[int]


@strawberry.input
class OrderedGraphAnchorBindingType:
    graph_anchor: GraphAnchorMutationType
    order: Optional[int]


@graphql_input(Graph, inject_mixin_fields=[UUIDMixin, StatusMixin], partial=True)
class GraphMutationType:
    graph_anchor: GraphAnchor
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


@graphql_input(
    Code,
    inject_mixin_fields=[UUIDMixin],
    partial=True,
)
class CodeMutationType:
    name: str
    code: str
    tutorial_anchor: TutorialAnchorMutationType


@graphql_input(
    ExecutionResult,
    inject_mixin_fields=[UUIDMixin],
    partial=True,
)
class ExecutionResultMutationType:
    code: CodeMutationType
    graph_anchor: GraphAnchorMutationType
    result_json: str
    result_json_meta: str


@strawberry.enum
class OperationType(enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
