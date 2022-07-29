from __future__ import annotations

from copy import copy
from uuid import UUID

from django.db.models import QuerySet
from strawberry import UNSET
from typing import List, Dict, Optional

from django.core.validators import validate_slug
from django.http import HttpRequest

from . import ValidationError, TagAnchorBridge, text_processing_wrapper
from .version_handlers import should_create_new_version, IMPOSSIBLE
from ..data_bridge import DataBridgeBase
from ..models import (
    TutorialAnchor,
    UserRoles,
    User,
    Tutorial,
    GraphAnchor,
    OrderedAnchorTable,
)
from ..types import (
    TutorialAnchorMutationType,
    TagAnchorMutationType,
    TutorialMutationType,
    UserMutationType,
    OrderedGraphAnchorBindingType,
)


class TutorialAnchorBridge(DataBridgeBase[TutorialAnchor, TutorialAnchorMutationType]):
    __slots__ = ()

    _bridged_model_cls = TutorialAnchor
    _require_edit_authentication = True
    _minimal_edit_user_role = UserRoles.AUTHOR

    @text_processing_wrapper()
    def _bridges_url(self, url: str, *_, **__) -> None:
        validate_slug(url)

        self._model_instance.url = url

    @text_processing_wrapper()
    def _bridges_anchor_name(self, anchor_name: str, *_, **__) -> None:
        self._model_instance.anchor_name = anchor_name

    def _bridges_tag_anchors(
        self,
        tag_anchors: List[TagAnchorMutationType],
        *_,
        request: HttpRequest = None,
        **__,
    ) -> None:
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
        **__,
    ) -> None:
        ordered_graph_anchor_bindings = graph_anchors  # rename for clarity

        graph_anchor_instances = GraphAnchor.objects.filter(
            id__in=[
                ordered_anchor_binding.graph_anchor.id
                for ordered_anchor_binding in ordered_graph_anchor_bindings
            ]
        )

        self._model_instance.graph_anchors.set(graph_anchor_instances)

        ordered_anchor_id_bindings: Dict[UUID, OrderedAnchorTable] = {
            binding.graph_anchor.id: binding
            for binding in OrderedAnchorTable.objects.filter(
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
    __slots__ = ()

    _bridged_model_cls = Tutorial
    _attaching_to = "tutorial_anchor"
    _require_edit_authentication = True
    _minimal_edit_user_role = UserRoles.TRANSLATOR

    def _bridges_tutorial_anchor(
        self,
        tutorial_anchor: TutorialAnchorMutationType,
        *_,
        request: HttpRequest = None,
        **__,
    ) -> None:
        if tutorial_anchor is UNSET:
            raise ValidationError("Tutorial anchor is required.")

        bridge = TutorialAnchorBridge.bridges_from_model_info(
            tutorial_anchor, request=request
        )
        self._model_instance.tutorial_anchor = bridge._model_instance

    def _bridges_authors(self, authors: List[UserMutationType], *_, **__) -> None:
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
    def _bridges_title(self, title: str, *_, **__) -> None:
        self._model_instance.title = title

    @text_processing_wrapper()
    def _bridges_abstract(self, abstract: str, *_, **__) -> None:
        self._model_instance.abstract = abstract

    @text_processing_wrapper()  # TODO: maybe no text processing for text content?
    def _bridges_content_markdown(
        self,
        content_markdown: str,
        *_,
        **__,
    ) -> None:
        self._model_instance.content_markdown = content_markdown

    @classmethod
    def _create_op(
        cls,
        bridge_instance: TutorialBridge,
        model_info: TutorialMutationType,
        *,
        request: Optional[HttpRequest] = None,
        **kwargs,
    ):
        raise RuntimeError("Tutorials cannot be created.")

    @classmethod
    def _update_op(
        cls,
        bridge_instance: TutorialBridge,
        model_info: TutorialMutationType,
        *,
        request: Optional[HttpRequest] = None,
        **kwargs,
    ):
        if cls.bridged_model_cls.objects.filter(
            id=bridge_instance.model_instance.id
        ).exists():
            # if the object is specified, then we are updating it
            bridge_instance.bridges_model_info(model_info, request=request)
            return

        # otherwise, we let the system handle it
        head_objects: QuerySet = cls.bridged_model_cls.objects.filter(
            tutorial_anchor__url=model_info.tutorial_anchor.url, front=None
        )
        head_count = head_objects.count()

        # count the number of heads
        if head_count > 1:
            # the there are multiple heads, then there is abnormality in the database.
            # admin should be called to handle this
            raise RuntimeError(
                f"Multiple heads exist in '{model_info.tutorial_anchor.url}', which is not supported"
            )
        elif head_count == 1:
            # if there is one head, then we check if we need to create a new head
            # or update it
            head_object = head_objects.first()
            new_version_status = should_create_new_version(
                head_object, request, model_info
            )

            if new_version_status is IMPOSSIBLE:
                raise RuntimeError(
                    f"{cls.__name__} cannot create new version for '{model_info.tutorial_anchor.url}' "
                    f"based on the current state and the request. \n"
                    f"head status: {head_object.item_status}\n"
                    f"request status: {model_info.item_status}\n"
                    f"request is empty? {request is None}"
                )
            elif new_version_status is None:
                bridge_instance.bridges_model_info(
                    model_info, request=request, **kwargs
                )
            else:
                old_bridge_instance = copy(bridge_instance)
                bridge_instance._ident = UNSET
                bridge_instance.get_instance().bridges_field(
                    "back", old_bridge_instance.model_instance, request=request
                )
                bridge_instance.bridges_model_info(
                    model_info, request=request, **kwargs
                )

        elif head_count == 0:
            bridge_instance.bridges_model_info(model_info, request=request, **kwargs)
        else:
            # this won't happen though
            raise RuntimeError(
                f"Unexpected head count in '{bridge_instance.model_instance}'"
            )
