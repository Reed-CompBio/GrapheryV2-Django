from __future__ import annotations

from typing import List, Optional
from uuid import UUID

import strawberry
from django.contrib.auth import get_user_model
from strawberry.types import Info

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
    LangCode,
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
    tutorials: List[TutorialAnchorType]
    graphs: List[GraphAnchorType]
    graph_descriptions: List[GraphDescriptionType]


@graphql_type(TagAnchor)
class TagAnchorType:
    anchor_name: str
    tags: List[TagType]
    # reverse relations
    tutorial_anchors: List[TutorialAnchorType]
    graph_anchors: List[GraphAnchorType]


@graphql_type(Tag)
class TagType:
    name: str
    tag_anchor: TagAnchorType
    description: str


@graphql_type(TutorialAnchor)
class TutorialAnchorType:
    url: str
    anchor_name: str
    tag_anchors: List[TagAnchorType]
    # reverse relation
    tutorials: List[TutorialType]
    graph_anchors: List[GraphAnchorType]
    code: Optional[CodeType]
    uploads: List[UploadsType]


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
    tags: List[TagAnchorType]
    default_order: int
    tutorial_anchors: List[OrderedGraphAnchorType]
    # reverse relations
    graph: Optional[GraphType]
    graph_descriptions: List[GraphDescriptionType]
    execution_results: List[ExecutionResultType]
    uploads: List[UploadsType]

    @strawberry.field
    def graph_description(
        self, info: Info, lang: LangCode = LangCode.EN
    ) -> Optional[GraphDescriptionType]:
        if qs := GraphDescription.objects.filter(graph_anchor=self, lang_code=lang):
            return qs[0]
        elif qs := GraphDescription.objects.filter(
            graph_anchor=self, lang_code=LangCode.EN
        ):
            return qs[0]
        else:
            return None

    @strawberry.field
    def execution_result(
        self, info: Info, code_id: UUID
    ) -> Optional[ExecutionResultType]:
        return (
            qs[0]
            if (
                qs := ExecutionResult.objects.filter(
                    graph_anchor=self, code__id=code_id
                )
            )
            else None
        )


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
    execution_results: List[ExecutionResultType]

    @strawberry.field
    def execution_result(
        self, info: Info, graph_anchor_id: UUID
    ) -> Optional[ExecutionResultType]:
        return (
            qs[0]
            if (
                qs := ExecutionResult.objects.filter(
                    code=self, graph_anchor__id=graph_anchor_id
                )
            )
            else None
        )


@graphql_type(ExecutionResult)
class ExecutionResultType:
    code: CodeType
    graph_anchor: GraphAnchorType
    result_json: str
    result_json_meta: str


@graphql_type(Uploads)
class UploadsType:
    name: str
    tutorial_anchors: List[TutorialAnchorType]
    graph_anchors: List[GraphAnchorType]
