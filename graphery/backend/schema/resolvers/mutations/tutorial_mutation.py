from __future__ import annotations

from strawberry.types import Info

from ....data_bridge import TutorialAnchorBridge, TutorialBridge
from ....types import (
    OperationType,
    TutorialAnchorMutationType,
    TutorialAnchorType,
    TutorialMutationType,
    TutorialType,
)

__all__ = ["tutorial_anchor_mutation", "tutorial_mutation"]


def tutorial_anchor_mutation(
    info: Info, op: OperationType, data: TutorialAnchorMutationType
) -> TutorialAnchorType:
    return TutorialAnchorBridge.bridges_from_mutation(op, data, info=info)


def tutorial_mutation(
    info: Info, op: OperationType, data: TutorialMutationType
) -> TutorialType:
    return TutorialBridge.bridges_from_mutation(op, data, info=info)
