from __future__ import annotations

from typing import Optional

from django.http import HttpRequest

from . import DataBridgeBase, ValidationError
from ..models import TagAnchor, User, UserRoles, Tag
from ..types import TagAnchorMutationType, TagMutationType

__all__ = ["TagAnchorBridge", "TagBridge"]


class TagAnchorBridge(DataBridgeBase[TagAnchor, TagAnchorMutationType]):
    _bridged_model = TagAnchor

    def _has_basic_permission(self, request: HttpRequest) -> bool:
        user: User = request.user
        return user.is_authenticated and user.role >= UserRoles.AUTHOR

    def _bridges_anchor_name(
        self, anchor_name, *_, request: HttpRequest = None, **__
    ) -> None:
        if not self._has_basic_permission(request=request):
            raise ValidationError(
                "You do not have permission to create/change a tag anchor."
            )

        anchor_name = anchor_name.strip()

        self._model_instance.anchor_name = anchor_name
        self._model_instance.save()


class TagBridge(DataBridgeBase[Tag, TagMutationType]):
    _bridged_model = Tag

    def _has_basic_permission(self, request: HttpRequest) -> bool:
        user: User = request.user
        return user.is_authenticated and user.role >= UserRoles.AUTHOR

    def _bridges_name(self, name, *_, request: HttpRequest = None, **__) -> None:
        if not self._has_basic_permission(request):
            raise ValidationError(
                "You do not have permission to create/change a tag's name."
            )

        name = name.strip()

        self._model_instance.name = name
        self._model_instance.save()

    def _bridges_tag_anchor(
        self,
        tag_anchor: Optional[TagAnchorMutationType],
        *_,
        request: HttpRequest = None,
        **__,
    ) -> None:
        if not self._has_basic_permission(request):
            raise ValidationError("You do not have permission to link tag to anchors.")

        if tag_anchor is not None:
            bridge = TagAnchorBridge.bridges_from_model_info(
                tag_anchor, request=request
            )
            self._model_instance.tag_anchor = bridge._model_instance
            self._model_instance.save()

    def _bridges_description(
        self, description: str, *_, request: HttpRequest = None, **__
    ) -> None:
        if not self._has_basic_permission(request):
            raise ValidationError(
                "You do not have permission to create/change a tag description."
            )

        description = description.strip()

        self._model_instance.description = description
        self._model_instance.save()
