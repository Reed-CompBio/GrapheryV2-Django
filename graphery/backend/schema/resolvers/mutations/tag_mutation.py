from __future__ import annotations

from typing import Optional

from strawberry.types import Info

from ....data_bridge import TagAnchorBridge, TagBridge
from ....types import TagAnchorType
from ....types.django_inputs import (
    OperationType,
    TagAnchorMutationType,
    TagMutationType,
)


__all__ = ["tag_anchor_mutation", "tag_mutation"]


def tag_anchor_mutation(
    info: Info, op: OperationType, data: TagAnchorMutationType
) -> Optional[TagAnchorType]:
    return TagAnchorBridge.bridges_from_mutation(op, data, info=info)


def tag_mutation(
    info: Info, op: OperationType, data: TagMutationType
) -> Optional[TagAnchorType]:
    return TagBridge.bridges_from_mutation(op, data, info=info)
