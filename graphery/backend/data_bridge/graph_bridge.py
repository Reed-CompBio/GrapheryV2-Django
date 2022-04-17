from __future__ import annotations

from typing import List, Dict
from uuid import UUID

from django.core.validators import validate_slug
from django.http import HttpRequest

from . import TagAnchorBridge
from .base import text_processing_wrapper
from ..data_bridge import DataBridgeBase
from ..models import GraphAnchor, UserRoles, OrderedGraphAnchor, TutorialAnchor
from ..types import (
    GraphAnchorMutationType,
    TagAnchorMutationType,
    OrderedTutorialAnchorBindingType,
)


class GraphAnchorBridge(DataBridgeBase[GraphAnchor, GraphAnchorMutationType]):
    _bridged_model = GraphAnchor
    _require_authentication = True
    _minimal_user_role = UserRoles.AUTHOR

    @text_processing_wrapper()
    def _bridges_url(self, url: str, *_, request: HttpRequest = None, **__) -> None:
        self._has_basic_permission(
            request,
            "You do not have permission to edit the url of a graph anchor.",
        )

        validate_slug(url)

        self._model_instance.url = url

    @text_processing_wrapper()
    def _bridges_anchor_name(
        self, anchor_name: str, *_, request: HttpRequest = None, **__
    ) -> None:
        self._has_basic_permission(
            request,
            "You do not have permission to edit the name of a graph anchor.",
        )

        self._model_instance.anchor_name = anchor_name

    def _bridges_tag_anchors(
        self,
        tag_anchors: List[TagAnchorMutationType],
        *_,
        request: HttpRequest = None,
        **__,
    ) -> None:
        self._has_basic_permission(
            request,
            "You do not have permission to edit tags of a graph anchor.",
        )

        tag_anchor_instances = [
            TagAnchorBridge.bridges_from_model_info(
                tag_anchor_info, request=request
            )._model_instance
            for tag_anchor_info in tag_anchors
        ]

        self._model_instance.tag_anchors.set(tag_anchor_instances)

    def _bridges_default_order(
        self, default_order: int, *_, request: HttpRequest = None, **__
    ) -> None:
        self._has_basic_permission(
            request,
            "You do not have permission to edit default order of a graph anchor.",
        )

        self._model_instance.default_order = default_order

    def _bridges_tutorial_anchors(
        self,
        tutorial_anchors: List[OrderedTutorialAnchorBindingType],
        *_,
        request: HttpRequest = None,
        **__,
    ) -> None:
        """
        This method is used to bind the tutorial anchors to the graph anchor.
        The input info is in type of `OrderedTutorialAnchorBindingType` instead of
        `TutorialAnchorMutationType` since we are also ordering the order of each
        graph anchor.
        :param tutorial_anchors:
        :param _:
        :param request:
        :param __:
        :return:
        """
        self._has_basic_permission(
            request,
            "You do not have permission to edit tutorials of a graph anchor.",
        )

        ordered_tutorial_anchor_bindings = tutorial_anchors  # rename for clarity

        # get the tutorial anchor instances
        # this does not require bridging since
        # modifying tutorial while editing graph anchor is not allowed
        tutorial_anchor_instances = TutorialAnchor.objects.filter(
            id__in=[
                binding.tutorial_anchor.id
                for binding in ordered_tutorial_anchor_bindings
            ]
        )

        # set the graph anchor's tutorial anchor link to the tutorial anchor instances above
        self._model_instance.tutorial_anchors.set(tutorial_anchor_instances)

        # find ordered record for each tutorial anchor,
        # and make a tutorial anchor id <-> ordered anchor mapping
        ordered_anchor_id_bindings: Dict[UUID, OrderedGraphAnchor] = {
            binding.tutorial_anchor.id: binding
            for binding in OrderedGraphAnchor.objects.filter(
                tutorial_anchor__in=tutorial_anchor_instances
            )
        }

        for ordered_anchor_info in ordered_tutorial_anchor_bindings:
            # search for the ordered record for the tutorial anchor
            binding = ordered_anchor_id_bindings.get(
                ordered_anchor_info.tutorial_anchor.id, None
            )
            if binding is None:
                # if the record is not found, raise
                raise ValueError(
                    f"Tutorial anchor {ordered_anchor_info.tutorial_anchor.id} is not bound to this graph anchor."
                )
            # otherwise, update the order of the record and save the record
            binding.order = ordered_anchor_info.order
            binding.save()
