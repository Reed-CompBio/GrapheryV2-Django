from __future__ import annotations

import strawberry
from uuid import UUID

from typing import List, Optional, Sequence

from strawberry.types import Info

from ..models import TagAnchor, TutorialAnchor, GraphAnchor
from ..types import (
    TagAnchorType,
    UserType,
    TutorialAnchorType,
    GraphAnchorType,
)

__all__ = [
    "resolve_current_user",
    "resolve_tag_anchors",
    "resolve_tutorial_anchors",
    "resolve_graph_anchors",
]


def resolve_current_user(info: Info) -> Optional[UserType]:
    if not info.context.request.user.is_authenticated:
        return None
    return info.context.request.user


def resolve_tag_anchors(
    info: Info, ids: Optional[List[Optional[strawberry.ID]]] = None
) -> List[Optional[TagAnchorType]]:
    if ids:
        if isinstance(ids, Sequence):
            uuids = [UUID(ident) for ident in ids]
            return TagAnchor.objects.filter(id__in=uuids)

    return TagAnchor.objects.all()


def resolve_tutorial_anchors(
    info: Info, ids: Optional[List[Optional[strawberry.ID]]]
) -> List[Optional[TutorialAnchorType]]:
    if ids:
        if isinstance(ids, Sequence):
            uuids = [UUID(ident) for ident in ids]
            return TutorialAnchor.objects.filter(id__in=uuids)
    return TutorialAnchor.objects.all()


def resolve_graph_anchors(
    info: Info, ids: Optional[List[Optional[strawberry.ID]]]
) -> List[Optional[GraphAnchorType]]:
    if ids:
        if isinstance(ids, Sequence):
            uuids = [UUID(ident) for ident in ids]
            return GraphAnchor.objects.filter(id__in=uuids)
    return GraphAnchor.objects.all()
