from __future__ import annotations

from typing import List, Optional

from django.contrib.auth import get_user_model

from . import graphql_type

from ..models import (
    TagAnchor,
    Tag,
    TutorialAnchor,
    Tutorial,
    GraphAnchor,
    OrderedAnchorTable,
    Graph,
    GraphDescription,
    Code,
    ExecutionResult,
    Uploads,
)

__all__ = [
    "UserType",
    "TagAnchorType",
    "TagType",
    "TutorialAnchorType",
    "TutorialType",
    "GraphAnchorType",
    "GraphType",
    "OrderedGraphAnchorType",
    "GraphDescriptionType",
    "CodeType",
    "ExecutionResultType",
    "UploadsType",
]


@graphql_type(get_user_model())
class UserType:
    username: str
    email: str
    displayed_name: str
    role: int
    is_staff: bool
    # reverse relations
    tutorials: List[Optional[TutorialAnchorType]]
    graphs: List[Optional[GraphAnchorType]]
    graph_descriptions: List[Optional[GraphDescriptionType]]


@graphql_type(TagAnchor)
class TagAnchorType:
    anchor_name: str
    tags: List[Optional[TagType]]
    # reverse relations
    tutorial_anchors: List[Optional[TutorialAnchorType]]
    graph_anchors: List[Optional[GraphAnchorType]]


@graphql_type(Tag)
class TagType:
    name: str
    tag_anchor: TagAnchorType
    description: str


@graphql_type(TutorialAnchor)
class TutorialAnchorType:
    url: str
    anchor_name: str
    tag_anchors: List[Optional[TagAnchorType]]
    # reverse relation
    tutorials: List[Optional[TutorialType]]
    graph_anchors: List[Optional[GraphAnchorType]]
    code: Optional[CodeType]
    uploads: List[Optional[UploadsType]]


@graphql_type(Tutorial)
class TutorialType:
    tutorial_anchor: TutorialAnchorType
    authors: List[UserType]
    title: str
    abstract: str
    content_markdown: str


@graphql_type(GraphAnchor)
class GraphAnchorType:
    url: str
    anchor_name: str
    tags: List[Optional[TagAnchorType]]
    default_order: int
    tutorial_anchors: List[Optional[OrderedGraphAnchorType]]
    # reverse relations
    graph: Optional[GraphType]
    graph_descriptions: List[Optional[GraphDescriptionType]]
    execution_results: List[Optional[ExecutionResultType]]
    uploads: List[Optional[UploadsType]]


@graphql_type(OrderedAnchorTable)
class OrderedGraphAnchorType:
    graph_anchor: GraphAnchorType
    tutorial_anchor: TutorialAnchorType
    order: int


@graphql_type(Graph)
class GraphType:
    graph_anchor: GraphAnchorType
    graph_json: str
    makers: List[UserType]


@graphql_type(GraphDescription)
class GraphDescriptionType:
    graph_anchor: GraphAnchorType
    authors: List[UserType]
    title: str
    description_markdown: str


@graphql_type(Code)
class CodeType:
    name: str
    code: str
    tutorial_anchor: TutorialAnchorType
    # reverse relation
    execution_results: List[Optional[ExecutionResultType]]


@graphql_type(ExecutionResult)
class ExecutionResultType:
    code: CodeType
    graph_anchor: GraphAnchorType
    result_json: str
    result_json_meta: str


@graphql_type(Uploads)
class UploadsType:
    name: str
    tutorial_anchors: List[Optional[TutorialAnchorType]]
    graph_anchors: List[Optional[GraphAnchorType]]
