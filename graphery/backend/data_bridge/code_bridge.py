from __future__ import annotations

import black
from django.http import HttpRequest
from strawberry.arguments import UNSET

from . import ValidationError
from ..data_bridge import DataBridgeBase, text_processing_wrapper
from ..models import Code, UserRoles, TutorialAnchor
from ..types import (
    CodeMutationType,
    TutorialAnchorMutationType,
)

__all__ = ["CodeBridge"]


class CodeBridge(DataBridgeBase[Code, CodeMutationType]):
    _bridged_model = Code
    _require_authentication = True
    _minimal_user_role = UserRoles.AUTHOR
    _attaching_to = "tutorial_anchor"

    @text_processing_wrapper()
    def _bridges_name(self, name: str, *_, request: HttpRequest = None, **__) -> None:
        self._has_basic_permission(
            request, "You don't have permission to change the name of this code."
        )

        self._model_instance.name = name

    def _bridges_code(self, code: str, *_, request: HttpRequest = None, **__) -> None:
        # black code before saving
        self._has_basic_permission(
            request,
            "You don't have permission to change the code content of this code.",
        )

        self._model_instance.code = black.format_str(
            code,
            mode=black.Mode(
                target_versions=black.TargetVersion.PY310,
                line_length=120,
            ),
        )

    def _bridges_tutorial_anchor(
        self,
        tutorial_anchor: TutorialAnchorMutationType,
        *_,
        request: HttpRequest = None,
        **__,
    ) -> None:
        self._has_basic_permission(
            request,
            "You don't have permission to change the tutorial anchor of this code.",
        )
        if tutorial_anchor is UNSET:
            raise ValidationError("TutorialAnchor for Code is required.")

        # get only
        self._model_instance.tutorial_anchor = TutorialAnchor.objects.get(
            id=tutorial_anchor.id
        )