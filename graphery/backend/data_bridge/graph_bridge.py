from __future__ import annotations

from typing import List

from django.core.validators import validate_slug
from django.http import HttpRequest

from . import TagAnchorBridge, TutorialAnchorBridge
from .base import text_processing_wrapper
from ..data_bridge import DataBridgeBase
from ..models import GraphAnchor, UserRoles, OrderedGraphAnchor
from ..types import (
    GraphAnchorMutationType,
    TagAnchorMutationType,
    TutorialAnchorMutationType,
)


class GraphAnchorBridge(DataBridgeBase[GraphAnchor, GraphAnchorMutationType]):
    _bridged_model = GraphAnchor
    _require_authentication = True
    _minimal_user_role = UserRoles.AUTHOR

    @text_processing_wrapper()
    def _bridges_url(self, url: str, *_, request: HttpRequest = None, **__) -> None:
        self._has_basic_permission(
            request, "You do not have permission to edit the url of a graph anchor."
        )

        validate_slug(url)

        self._model_instance.url = url

    @text_processing_wrapper()
    def _bridges_anchor_name(
        self, anchor_name: str, *_, request: HttpRequest = None, **__
    ) -> None:
        self._has_basic_permission(
            request, "You do not have permission to edit the name of a graph anchor."
        )

        self._model_instance.anchor_name = anchor_name

    def _bridges_tag_anchors(
        self,
        tag_anchors: List[TagAnchorMutationType],
        *_,
        request: HttpRequest = None,
        **__,
    ) -> None:
        self._has_basic_permission(
            request, "You do not have permission to edit tags of a graph anchor."
        )

        tag_anchor_instances = [
            TagAnchorBridge.bridges_from_model_info(tag_anchor_info)._model_instance
            for tag_anchor_info in tag_anchors
        ]

        self._model_instance.tag_anchors.set(tag_anchor_instances)

    def _bridges_default_order(
        self, default_order: int, *_, request: HttpRequest = None, **__
    ) -> None:
        self._has_basic_permission(
            request,
            "You do not have permission to edit default order of a graph anchor.",
        )

        self._model_instance.default_order = default_order

    def _bridges_tutorial_anchors(
        self,
        tutorial_anchors: List[TutorialAnchorMutationType],
        *_,
        request: HttpRequest = None,
        **__,
    ) -> None:
        self._has_basic_permission(
            request, "You do not have permission to edit tutorials of a graph anchor."
        )

        tutorial_anchor_instances = [
            TutorialAnchorBridge.bridges_from_model_info(
                tutorial_anchor_info
            )._model_instance
            for tutorial_anchor_info in tutorial_anchors
        ]

        self._model_instance.tutorial_anchors.set(tutorial_anchor_instances)
