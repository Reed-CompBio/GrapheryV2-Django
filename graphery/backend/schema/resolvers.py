from __future__ import annotations

from typing import List, Optional

from strawberry.types import Info

from ..models import TagAnchor, TutorialAnchor, GraphAnchor
from ..types import TagAnchorType, UserType, TutorialAnchorType, GraphAnchorType

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


def resolve_tag_anchors(info: Info) -> List[Optional[TagAnchorType]]:
    return TagAnchor.objects.all()


def resolve_tutorial_anchors(info: Info) -> List[Optional[TutorialAnchorType]]:
    return TutorialAnchor.objects.all()


def resolve_graph_anchors(info: Info) -> List[Optional[GraphAnchorType]]:
    return GraphAnchor.objects.all()
