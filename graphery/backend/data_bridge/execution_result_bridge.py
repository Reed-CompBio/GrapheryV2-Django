from __future__ import annotations

from typing import Dict

from strawberry import UNSET

from . import ValidationError
from .base import json_validation_wrapper
from ..data_bridge import DataBridgeBase
from ..models import ExecutionResult, UserRoles, Code, GraphAnchor
from ..types import (
    ExecutionResultMutationType,
    CodeMutationType,
    GraphAnchorMutationType,
)

__all__ = ["ExecutionResultBridge"]


class ExecutionResultBridge(
    DataBridgeBase[ExecutionResult, ExecutionResultMutationType]
):
    __slots__ = ()

    _bridged_model_cls = ExecutionResult
    _require_authentication = True
    _minimal_user_role = UserRoles.AUTHOR
    _attaching_to = ("code", "graph_anchor")

    def _bridges_code(self, code: CodeMutationType, *_, **__) -> None:
        """
        This is a special case
        we don't recursively instantiate a Code instance
        since modifying execution result should not change the code
        :param code:
        :param _:
        :param __:
        :return:
        """
        if code is UNSET:
            raise ValidationError("Code is required when setting ExecutionResult")

        self._model_instance.code = Code.objects.get(id=code.id)

    def _bridges_graph_anchor(
        self,
        graph_anchor: GraphAnchorMutationType,
        *_,
        **__,
    ) -> None:
        """
        This is a special case
        we don't recursively instantiate a GraphAnchor instance
        since modifying execution result should not change the graph anchor
        :param graph_anchor:
        :param _:
        :param __:
        :return:
        """
        if graph_anchor is UNSET:
            raise ValidationError(
                "Graph anchor is required when setting ExecutionResult"
            )

        self._model_instance.graph_anchor = GraphAnchor.objects.get(id=graph_anchor.id)

    @json_validation_wrapper
    def _bridges_result_json(self, result_json: Dict, *_, **__) -> None:
        if not isinstance(result_json, dict):
            raise ValidationError(
                f"result_json has to be a dict or a string of dict, but got {result_json}"
            )

        self._model_instance.result_json = result_json

    @json_validation_wrapper
    def _bridges_result_json_meta(self, result_json_meta: Dict, *_, **__) -> None:
        if not isinstance(result_json_meta, dict):
            raise ValidationError(
                f"result_json_meta has to be a dict or a string of dict, but got {result_json_meta}"
            )

        self._model_instance.result_json_meta = result_json_meta
