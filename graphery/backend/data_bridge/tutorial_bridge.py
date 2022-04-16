from __future__ import annotations

from strawberry.arguments import UNSET
from typing import List

from django.core.validators import validate_slug
from django.http import HttpRequest

from . import ValidationError, TagAnchorBridge, text_processing_wrapper
from ..data_bridge import DataBridgeBase
from ..models import TutorialAnchor, UserRoles, User, Tutorial
from ..types import (
    TutorialAnchorMutationType,
    TagAnchorMutationType,
    TutorialMutationType,
    UserMutationType,
)


class TutorialAnchorBridge(DataBridgeBase[TutorialAnchor, TutorialAnchorMutationType]):
    _bridged_model = TutorialAnchor

    _require_authentication = True
    _minimal_user_role = UserRoles.AUTHOR

    @text_processing_wrapper()
    def _bridges_url(self, url: str, *_, request: HttpRequest = None, **__) -> None:
        self._has_basic_permission(request)

        validate_slug(url)

        self._model_instance.url = url

    @text_processing_wrapper()
    def _bridges_anchor_name(
        self, anchor_name: str, *_, request: HttpRequest = None, **__
    ) -> None:
        self._has_basic_permission(request)

        self._model_instance.anchor_name = anchor_name

    def _bridges_tag_anchors(
        self,
        tag_anchors: List[TagAnchorMutationType],
        *_,
        request: HttpRequest = None,
        **__,
    ) -> None:
        self._has_basic_permission(request)

        tag_anchor_instances = [
            TagAnchorBridge.bridges_from_model_info(
                tag_anchor_info, request=request
            )._model_instance
            for tag_anchor_info in tag_anchors
        ]

        self._model_instance.tag_anchors.set(tag_anchor_instances)


class TutorialBridge(DataBridgeBase[Tutorial, TutorialMutationType]):
    _bridged_model = Tutorial
    _attaching_to = "tutorial_anchor"

    _require_authentication = True
    _minimal_user_role = UserRoles.TRANSLATOR

    def _bridges_tutorial_anchor(
        self,
        tutorial_anchor: TutorialAnchorMutationType,
        *_,
        request: HttpRequest = None,
        **__,
    ) -> None:
        self._has_basic_permission(request)

        if tutorial_anchor is UNSET:
            raise ValidationError("Tutorial anchor is required.")

        bridge = TutorialAnchorBridge.bridges_from_model_info(
            tutorial_anchor, request=request
        )
        self._model_instance.tutorial_anchor = bridge._model_instance

    def _bridges_authors(
        self, authors: List[UserMutationType], *_, request: HttpRequest = None, **__
    ) -> None:
        self._has_basic_permission(request)

        author_instances = list(
            User.objects.filter(id__in=[author.id for author in authors])
        )
        for author_instance in author_instances:
            if author_instance.role < UserRoles.TRANSLATOR:
                raise ValidationError(
                    f"User {author_instance.username} is does not have the permission "
                    f"to edit the tutorial {self._model_instance.title}."
                )

        self._model_instance.authors.set(author_instances)

    @text_processing_wrapper()
    def _bridges_title(self, title: str, *_, request: HttpRequest = None, **__) -> None:
        self._has_basic_permission(request)

        self._model_instance.title = title

    @text_processing_wrapper()
    def _bridges_abstract(
        self, abstract: str, *_, request: HttpRequest = None, **__
    ) -> None:
        self._has_basic_permission(request)

        self._model_instance.abstract = abstract

    @text_processing_wrapper()  # TODO: maybe no text processing for text content?
    def _bridges_content_markdown(
        self,
        content_markdown: str,
        *_,
        request: HttpRequest = None,
        **__,
    ) -> None:
        self._has_basic_permission(request)

        self._model_instance.content_markdown = content_markdown
