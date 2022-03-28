from __future__ import annotations

from django.http import HttpRequest

from . import DataBridgeBase, ValidationError
from ..models import TagAnchor, User, UserRoles
from ..types import TagAnchorType


class TagAnchorBridge(DataBridgeBase[TagAnchor, TagAnchorType]):
    _bridged_model = TagAnchor

    def _has_basic_permission(self, request: HttpRequest) -> bool:
        user: User = request.user
        return user.is_authenticated and user.role >= UserRoles.AUTHOR

    def _bridges_anchor_name(
        self, anchor_name, *args, request: HttpRequest = None, **kwargs
    ) -> None:
        if not self._has_basic_permission(request=request):
            raise ValidationError(
                "You do not have permission to create/change a tag anchor."
            )

        anchor_name = anchor_name.strip()

        self._model_instance.anchor_name = anchor_name
        self._model_instance.save()
