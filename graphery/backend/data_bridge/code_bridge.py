from __future__ import annotations

from functools import partial

import black
from strawberry import UNSET

from . import ValidationError
from ..data_bridge import DataBridgeBase, text_processing_wrapper
from ..models import Code, UserRoles, TutorialAnchor
from ..types import (
    CodeMutationType,
    TutorialAnchorMutationType,
)

__all__ = ["black_format_str", "CodeBridge"]

black_format_str = partial(
    black.format_str,
    mode=black.Mode(
        target_versions={black.TargetVersion.PY310},
        line_length=120,
    ),
)


class CodeBridge(DataBridgeBase[Code, CodeMutationType]):
    __slots__ = ()

    _bridged_model_cls = Code
    _require_authentication = True
    _minimal_user_role = UserRoles.AUTHOR
    _attaching_to = "tutorial_anchor"

    @text_processing_wrapper()
    def _bridges_name(self, name: str, *_, **__) -> None:
        self._model_instance.name = name

    def _bridges_code(self, code: str, *_, **__) -> None:
        # black code before saving
        self._model_instance.code = black_format_str(code)

    def _bridges_tutorial_anchor(
        self,
        tutorial_anchor: TutorialAnchorMutationType,
        *_,
        **__,
    ) -> None:
        if tutorial_anchor is UNSET:
            raise ValidationError("TutorialAnchor for Code is required.")

        # get only
        self._model_instance.tutorial_anchor = TutorialAnchor.objects.get(
            id=tutorial_anchor.id
        )
