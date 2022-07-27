from __future__ import annotations

from strawberry.types import Info

from ....data_bridge import GraphAnchorBridge, GraphBridge, GraphDescriptionBridge
from ....types import (
    OperationType,
    GraphAnchorMutationType,
    GraphType,
    GraphMutationType,
    GraphDescriptionType,
    GraphDescriptionMutationType,
    GraphAnchorType,
)


__all__ = ["graph_anchor_mutation", "graph_mutation", "graph_description_mutation"]


def graph_anchor_mutation(
    info: Info, op: OperationType, data: GraphAnchorMutationType
) -> GraphAnchorType:
    return GraphAnchorBridge.bridges_from_mutation(op, data, info=info)


def graph_mutation(info: Info, op: OperationType, data: GraphMutationType) -> GraphType:
    return GraphBridge.bridges_from_mutation(op, data, info=info)


def graph_description_mutation(
    info: Info, op: OperationType, data: GraphDescriptionMutationType
) -> GraphDescriptionType:
    return GraphDescriptionBridge.bridges_from_mutation(op, data, info=info)
