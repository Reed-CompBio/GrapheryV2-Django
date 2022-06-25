from __future__ import annotations

from time import sleep

import strawberry
from uuid import UUID

from typing import List, Optional, Sequence

from strawberry.types import Info

from ....models import TutorialAnchor, GraphAnchor, Tutorial, LangCode, Graph
from ....types import (
    UserType,
    TutorialAnchorType,
    GraphAnchorType,
    TutorialType,
    TutorialAnchorFilter,
    GraphAnchorFilter,
    GraphDescriptionType,
    GraphType,
)

__all__ = [
    "resolve_current_user",
    "resolve_tutorial_anchors",
    "get_tutorial_content",
    "get_graph_content",
    "get_graph_anchor",
    "resolve_graph_anchors",
]


def resolve_current_user(info: Info) -> Optional[UserType]:
    if not info.context.request.user.is_authenticated:
        return None
    return info.context.request.user


def resolve_tutorial_anchors(
    info: Info, filters: Optional[TutorialAnchorFilter] = None
) -> List[Optional[TutorialAnchorType]]:
    # TODO privilege check
    return TutorialAnchor.objects.all()


def resolve_graph_anchors(
    info: Info, filters: Optional[GraphAnchorFilter] = None
) -> List[Optional[GraphAnchorType]]:
    # TODO privilege check
    return GraphAnchor.objects.all()


def get_tutorial_content(
    info: Info, url: str, lang: LangCode = LangCode.EN
) -> Optional[TutorialType]:
    # TODO privilege check
    query_set = Tutorial.objects.filter(tutorial_anchor__url=url, lang_code=lang)
    return query_set[0] if query_set else None


def get_graph_content(
    info: Info,
    ids: Optional[List[Optional[strawberry.ID]]],
    urls: Optional[List[Optional[str]]],
    lang: LangCode = LangCode.EN,
) -> List[Optional[GraphDescriptionType]]:
    # TODO privilege check
    # TODO this might not be right
    query_set = GraphDescriptionType.objects.filter(
        graph_anchor__id__in=ids, lang_code=lang
    )
    return query_set


def get_graph_anchor(
    info: Info,
    ident: Optional[strawberry.ID],
) -> Optional[GraphType]:
    return Graph.objects.get(graph_anchor__id=ident)
