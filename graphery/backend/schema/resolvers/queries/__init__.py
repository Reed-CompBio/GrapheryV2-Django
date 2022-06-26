from __future__ import annotations

from uuid import UUID

from typing import List, Optional

from strawberry.types import Info

from ....models import (
    TutorialAnchor,
    GraphAnchor,
    Tutorial,
    LangCode,
    Graph,
    GraphDescription,
    Code,
)
from ....types import (
    UserType,
    TutorialAnchorType,
    GraphAnchorType,
    TutorialType,
    TutorialAnchorFilter,
    GraphAnchorFilter,
    GraphDescriptionType,
    GraphType,
    CodeType,
)

__all__ = [
    "resolve_current_user",
    "resolve_tutorial_anchors",
    "resolve_graph_anchors",
    "get_tutorial_content",
    "get_graph_content",
    "get_graph",
    "get_code",
]


def resolve_current_user(info: Info) -> Optional[UserType]:
    if not info.context.request.user.is_authenticated:
        return None
    return info.context.request.user


def resolve_tutorial_anchors(
    info: Info, filters: Optional[TutorialAnchorFilter] = None
) -> List[TutorialAnchorType]:
    # TODO privilege check
    return TutorialAnchor.objects.all()


def resolve_graph_anchors(
    info: Info, filters: Optional[GraphAnchorFilter] = None
) -> List[GraphAnchorType]:
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
    url: Optional[str],
    anchor_id: Optional[UUID],
    lang: LangCode = LangCode.EN,
) -> Optional[GraphDescriptionType]:
    if url:
        return GraphDescription.objects.filter(url=url, lang_code=lang)
    elif anchor_id:
        return GraphDescription.objects.filter(
            graph_anchor__id=anchor_id, lang_code=lang
        )
    else:
        return None


def get_graph(
    info: Info,
    anchor_id: UUID,
) -> Optional[GraphType]:
    return Graph.objects.get(graph_anchor__id=anchor_id)


def get_code(info: Info, code_id: UUID) -> Optional[CodeType]:
    return Code.objects.get(id=code_id)
