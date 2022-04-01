from __future__ import annotations

from strawberry.arguments import UNSET

from django.http import HttpRequest

from . import DataBridgeBase, ValidationError
from ..models import TagAnchor, User, UserRoles, Tag
from ..types import TagAnchorMutationType, TagMutationType

__all__ = ["TagAnchorBridge", "TagBridge"]


class TagAnchorBridge(DataBridgeBase[TagAnchor, TagAnchorMutationType]):
    _bridged_model = TagAnchor

    def _has_basic_permission(
        self, request: HttpRequest, error_msg: str = None
    ) -> None:
        super(TagAnchorBridge, self)._has_basic_permission(request, error_msg)

        user: User = request.user
        if not (user.is_authenticated and user.role >= UserRoles.AUTHOR):
            raise ValidationError(error_msg or self._default_permission_error_msg)

    def _bridges_anchor_name(
        self, anchor_name: str, *_, request: HttpRequest = None, **__
    ) -> None:
        self._has_basic_permission(
            request, "You do not have permission to create/change a tag anchor."
        )

        anchor_name = anchor_name.strip()

        self._model_instance.anchor_name = anchor_name


class TagBridge(DataBridgeBase[Tag, TagMutationType]):
    _bridged_model = Tag
    _attaching_to = "tag_anchor"

    def _has_basic_permission(
        self, request: HttpRequest, error_msg: str = None
    ) -> None:
        super(TagBridge, self)._has_basic_permission(request, error_msg)

        user: User = request.user
        if not (user.is_authenticated and user.role >= UserRoles.AUTHOR):
            raise ValidationError(error_msg or self._default_permission_error_msg)

    def _bridges_name(self, name, *_, request: HttpRequest = None, **__) -> None:
        self._has_basic_permission(
            request, "You do not have permission to create/change a tag's name."
        )

        name = name.strip()

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

    def _bridges_description(
        self, description: str, *_, request: HttpRequest = None, **__
    ) -> None:
        self._has_basic_permission(
            request, "You do not have permission to create/change a tag description."
        )

        description = description.strip()

        self._model_instance.description = description
