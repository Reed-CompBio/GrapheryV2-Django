from __future__ import annotations

from uuid import UUID

from strawberry.arguments import UNSET
from typing import List, Dict

from django.core.validators import validate_slug
from django.http import HttpRequest

from . import ValidationError, TagAnchorBridge, text_processing_wrapper
from ..data_bridge import DataBridgeBase
from ..models import (
    TutorialAnchor,
    UserRoles,
    User,
    Tutorial,
    GraphAnchor,
    OrderedGraphAnchor,
)
from ..types import (
    TutorialAnchorMutationType,
    TagAnchorMutationType,
    TutorialMutationType,
    UserMutationType,
    OrderedGraphAnchorBindingType,
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

    def _bridges_graph_anchors(
        self,
        graph_anchors: List[OrderedGraphAnchorBindingType],
        *_,
        request: HttpRequest = None,
        **__,
    ) -> None:
        self._has_basic_permission(
            request,
            "You do not have permission to edit graph anchors in this tutorial.",
        )

        ordered_graph_anchor_bindings = graph_anchors  # rename for clarity

        graph_anchor_instances = GraphAnchor.objects.filter(
            id__in=[
                ordered_anchor_binding.graph_anchor.id
                for ordered_anchor_binding in ordered_graph_anchor_bindings
            ]
        )

        self._model_instance.graph_anchors.set(graph_anchor_instances)

        ordered_anchor_id_bindings: Dict[UUID, OrderedGraphAnchor] = {
            binding.graph_anchor.id: binding
            for binding in OrderedGraphAnchor.objects.filter(
                graph_anchor__in=graph_anchor_instances
            )
        }

        for ordered_anchor_info in ordered_graph_anchor_bindings:
            binding = ordered_anchor_id_bindings.get(
                ordered_anchor_info.graph_anchor.id, None
            )

            if binding is None:
                raise ValidationError(
                    f"Graph anchor with id {ordered_anchor_info} does not exist in this tutorial."
                )
            binding.order = ordered_anchor_info.order
            binding.save()


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
