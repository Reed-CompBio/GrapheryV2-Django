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
        super(TagAnchorBridge, self)._has_basic_permission()
        user: User = request.user
        if not (user.is_authenticated and user.role >= UserRoles.AUTHOR):
            raise ValidationError(error_msg or self._default_permission_error_msg)

    def _bridges_anchor_name(
        self, anchor_name, *_, request: HttpRequest = None, **__
    ) -> None:
        self._has_basic_permission(
            request, "You do not have permission to create/change a tag anchor."
        )

        anchor_name = anchor_name.strip()

        self._model_instance.anchor_name = anchor_name
        self._model_instance.save()


class TagBridge(DataBridgeBase[Tag, TagMutationType]):
    _bridged_model = Tag

    def _has_basic_permission(
        self, request: HttpRequest, error_msg: str = None
    ) -> None:
        super(TagBridge, self)._has_basic_permission(request, error_msg)

        user: User = request.user
        if not (user.is_authenticated and user.role >= UserRoles.AUTHOR):
            raise ValidationError(error_msg or self._default_permission_error_msg)

    def bridges_model_info(
        self, model_info: TagMutationType, *, request: HttpRequest = None, **kwargs
    ) -> TagBridge:
        if model_info.tag_anchor is UNSET:
            self._bridges_tag_anchor(UNSET, request=request, **kwargs)
            self._ident = None
            self._model_instance = None
        else:
            super().bridges_model_info(model_info, request=request, **kwargs)

        return self

    def _bridges_name(self, name, *_, request: HttpRequest = None, **__) -> None:
        self._has_basic_permission(
            request, "You do not have permission to create/change a tag's name."
        )

        name = name.strip()

        self._model_instance.name = name
        self._model_instance.save()

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

        if tag_anchor is UNSET:
            # if the tag anchor is unset,
            # we want to unlink the tag from the anchor,
            # which subsequently deletes the tag
            # TODO: consider custom literal for delete?
            self._model_instance.delete()
        else:
            bridge = TagAnchorBridge.bridges_from_model_info(
                tag_anchor, request=request
            )
            self._model_instance.tag_anchor = bridge._model_instance
            self._model_instance.save()

    def _bridges_description(
        self, description: str, *_, request: HttpRequest = None, **__
    ) -> None:
        self._has_basic_permission(
            request, "You do not have permission to create/change a tag description."
        )

        description = description.strip()

        self._model_instance.description = description
        self._model_instance.save()
