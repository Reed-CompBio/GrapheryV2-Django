from __future__ import annotations

from strawberry.arguments import UNSET
from typing import List, Optional

from django.core.validators import validate_slug
from django.http import HttpRequest

from . import ValidationError, TagAnchorBridge
from ..data_bridge import DataBridgeBase
from ..models import TutorialAnchor, UserRoles, User, Tutorial
from ..types import (
    TutorialAnchorMutationType,
    TagAnchorMutationType,
    TutorialMutationType,
)


class TutorialAnchorBridge(DataBridgeBase[TutorialAnchor, TutorialAnchorMutationType]):
    _bridged_model = TutorialAnchor

    def _has_basic_permission(
        self, request: HttpRequest, error_msg: str = None
    ) -> None:
        super()._has_basic_permission(request)
        user: User = request.user
        if not (user.is_authenticated and user.role >= UserRoles.AUTHOR):
            raise ValidationError(error_msg or self._default_permission_error_msg)

    def _bridges_url(self, url: str, *_, request: HttpRequest = None, **__) -> None:
        self._has_basic_permission(request)

        url = url.strip()
        validate_slug(url)

        self._model_instance.url = url
        self._model_instance.save()

    def _bridges_anchor_name(
        self, anchor_name: str, *_, request: HttpRequest = None, **__
    ) -> None:
        self._has_basic_permission(request)

        anchor_name = anchor_name.strip()

        self._model_instance.anchor_name = anchor_name
        self._model_instance.save()

    def _bridges_tag_anchors(
        self,
        tag_anchors: List[Optional[TagAnchorMutationType]] * _,
        request: HttpRequest = None,
        **__,
    ) -> None:
        self._has_basic_permission(request)

        tag_anchor_instances = [
            TagAnchorBridge.bridges_from_model_info(tag_anchor_info)._model_instance
            for tag_anchor_info in tag_anchors
        ]

        self._model_instance.tag_anchors.set(tag_anchor_instances)
        self._model_instance.save()


class TutorialBridge(DataBridgeBase[Tutorial, TutorialMutationType]):
    _bridged_model = Tutorial

    def _has_basic_permission(
        self, request: HttpRequest, error_msg: str = None
    ) -> None:
        super()._has_basic_permission(request)
        user: User = request.user
        if not (user.is_authenticated and user.role >= UserRoles.TRANSLATOR):
            raise ValidationError(error_msg or self._default_permission_error_msg)

    def bridges_model_info(
        self, model_info: TutorialMutationType, *, request: HttpRequest = None, **kwargs
    ) -> TutorialBridge:
        if model_info.tutorial_anchor is UNSET:
            self._bridges_tutorial_anchor(UNSET, request=request, **kwargs)
        else:
            super(TutorialBridge, self).bridges_model_info(
                model_info, request=request, **kwargs
            )

        return self

    def _bridges_tutorial_anchor(
        self,
        tutorial_anchor: TutorialAnchorMutationType | UNSET,
        *_,
        request: HttpRequest = None,
        **__,
    ) -> None:
        if tutorial_anchor is UNSET:
            self._model_instance.delete()
            self._model_instance = None
            self._ident = None
        else:
            bridge = TutorialAnchorBridge.bridges_from_model_info(
                tutorial_anchor, request=request
            )
            self._model_instance.tutorial_anchor = bridge._model_instance
            self._model_instance.save()

    def _bridges_title(self, title: str, *_, request: HttpRequest = None, **__) -> None:
        self._has_basic_permission(request)

        title = title.strip()

        self._model_instance.title = title
        self._model_instance.save()

    def _bridges_abstract(
        self, abstract: str, *_, request: HttpRequest = None, **__
    ) -> None:
        self._has_basic_permission(request)

        abstract = abstract.strip()

        self._model_instance.abstract = abstract
        self._model_instance.save()

    def _bridges_content_markdown(
        self,
        content_markdown: str,
        *_,
        request: HttpRequest = None,
        **__,
    ) -> None:
        self._has_basic_permission(request)

        content_markdown = content_markdown.strip()

        self._model_instance.content_markdown = content_markdown
        self._model_instance.save()
