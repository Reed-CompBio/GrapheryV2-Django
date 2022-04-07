from __future__ import annotations

from strawberry.arguments import UNSET

from django.http import HttpRequest

from . import DataBridgeBase, text_processing_wrapper
from ..models import TagAnchor, UserRoles, Tag
from ..types import TagAnchorMutationType, TagMutationType

__all__ = ["TagAnchorBridge", "TagBridge"]


class TagAnchorBridge(DataBridgeBase[TagAnchor, TagAnchorMutationType]):
    _bridged_model = TagAnchor
    _require_authentication = True
    _minimal_user_role = UserRoles.AUTHOR

    @text_processing_wrapper()
    def _bridges_anchor_name(
        self, anchor_name: str, *_, request: HttpRequest = None, **__
    ) -> None:
        self._has_basic_permission(
            request, "You do not have permission to create/change a tag anchor."
        )

        self._model_instance.anchor_name = anchor_name


class TagBridge(DataBridgeBase[Tag, TagMutationType]):
    _bridged_model = Tag
    _attaching_to = "tag_anchor"

    _require_authentication = True
    _minimal_user_role = UserRoles.AUTHOR

    @text_processing_wrapper()
    def _bridges_name(self, name, *_, request: HttpRequest = None, **__) -> None:
        self._has_basic_permission(
            request, "You do not have permission to create/change a tag's name."
        )

        self._model_instance.name = name

    def _bridges_tag_anchor(
        self,
        tag_anchor: TagAnchorMutationType | UNSET,
        *_,
        request: HttpRequest = None,
        **__,
    ) -> None:
        self._has_basic_permission(
            request, "You do not have permission to link tag to anchors."
        )

        bridge = TagAnchorBridge.bridges_from_model_info(tag_anchor, request=request)
        self._model_instance.tag_anchor = bridge._model_instance

    @text_processing_wrapper()
    def _bridges_description(
        self, description: str, *_, request: HttpRequest = None, **__
    ) -> None:
        self._has_basic_permission(
            request, "You do not have permission to create/change a tag description."
        )

        self._model_instance.description = description
