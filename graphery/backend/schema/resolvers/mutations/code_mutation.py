from __future__ import annotations

from strawberry.types import Info

from ....data_bridge import CodeBridge
from ....types import OperationType, CodeMutationType, CodeType


__all__ = ["code_mutation"]


def code_mutation(info: Info, op: OperationType, data: CodeMutationType) -> CodeType:
    return CodeBridge.bridges_from_mutation(op, data, info=info)
