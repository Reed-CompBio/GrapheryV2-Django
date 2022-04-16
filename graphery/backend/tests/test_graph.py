from __future__ import annotations

from typing import Sequence

import pytest

from .utils import (
    USER_LIST,
    instance_to_model_info,
    bridge_test_helper,
    make_request_with_user,
)
from ..baker_recipes import (
    graph_anchor_recipe,
    tutorial_anchor_recipe,
    tag_anchor_recipe,
)
from ..data_bridge.graph_bridge import GraphAnchorBridge
from ..models import GraphOrder, UserRoles, User, GraphAnchor, TagAnchor
from ..types import (
    GraphAnchorMutationType,
    OrderedTutorialAnchorBindingType,
    TutorialAnchorMutationType,
)


@pytest.fixture
def graph_anchor(transactional_db):
    return graph_anchor_recipe.make(
        tutorial_anchors=tutorial_anchor_recipe.make(_quantity=3)
    )


@pytest.fixture
def tag_anchors(transactional_db):
    return tag_anchor_recipe.make(_quantity=3)


@pytest.fixture
def bunch_of_tutorial_anchors(transactional_db):
    return tutorial_anchor_recipe.make(_quantity=5)


@pytest.mark.parametrize("get_fixture", USER_LIST, indirect=True)
def test_graph_anchor(
    rf,
    graph_anchor: GraphAnchor,
    tag_anchors: Sequence[TagAnchor],
    bunch_of_tutorial_anchors: Sequence[TagAnchor],
    get_fixture: User,
):
    old_model_info: GraphAnchorMutationType = instance_to_model_info(
        graph_anchor, GraphAnchorMutationType, ignore_value="tutorial_anchors"
    )

    # yeah, this is an annoying edge case
    old_model_info.tutorial_anchors = [
        OrderedTutorialAnchorBindingType(
            instance_to_model_info(tutorial_anchor, TutorialAnchorMutationType),
            order=GraphOrder.LOW,  # this is the default value, maybe I should query OrderedGraphAnchor
        )
        for tutorial_anchor in graph_anchor.tutorial_anchors.all()
    ]

    new_model_info = GraphAnchorMutationType(
        id=old_model_info.id,
        url="https://new_url.com",
        anchor_name="new_anchor_name",
        tag_anchors=[*old_model_info.tag_anchors, *tag_anchors],
        default_order=GraphOrder.HIGH,
        tutorial_anchors=[
            OrderedTutorialAnchorBindingType(
                instance_to_model_info(tutorial_anchor, TutorialAnchorMutationType),
                order=GraphOrder.MEDIUM,
            )
            for tutorial_anchor in bunch_of_tutorial_anchors
        ],
    )

    request = make_request_with_user(rf, get_fixture)

    bridge_test_helper(
        GraphAnchorBridge,
        new_model_info,
        old_model_info,
        request=request,
        min_user_role=UserRoles.AUTHOR,
    )
