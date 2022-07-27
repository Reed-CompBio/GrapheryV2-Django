from __future__ import annotations

from strawberry import UNSET

from django.http import HttpRequest

from . import DataBridgeBase, text_processing_wrapper
from ..models import TagAnchor, UserRoles, Tag
from ..types import TagAnchorMutationType, TagMutationType

__all__ = ["TagAnchorBridge", "TagBridge"]


class TagAnchorBridge(DataBridgeBase[TagAnchor, TagAnchorMutationType]):
    __slots__ = ()

    _bridged_model_cls = TagAnchor
    _require_edit_authentication = True
    _minimal_edit_user_role = UserRoles.AUTHOR

    @text_processing_wrapper()
    def _bridges_anchor_name(self, anchor_name: str, *_, **__) -> None:
        self._model_instance.anchor_name = anchor_name


class TagBridge(DataBridgeBase[Tag, TagMutationType]):
    __slots__ = ()

    _bridged_model_cls = Tag
    _attaching_to = "tag_anchor"
    _require_edit_authentication = True
    _minimal_edit_user_role = UserRoles.AUTHOR

    @text_processing_wrapper()
    def _bridges_name(self, name, *_, **__) -> None:
        self._model_instance.name = name

    def _bridges_tag_anchor(
        self,
        tag_anchor: TagAnchorMutationType | UNSET,
        *_,
        request: HttpRequest = None,
        **__,
    ) -> None:
        bridge = TagAnchorBridge.bridges_from_model_info(tag_anchor, request=request)
        self._model_instance.tag_anchor = bridge._model_instance

    @text_processing_wrapper()
    def _bridges_description(self, description: str, *_, **__) -> None:
        self._model_instance.description = description
