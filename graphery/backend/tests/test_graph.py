from __future__ import annotations

import json
from typing import Sequence, List, Dict

import pytest

from .utils import (
    USER_LIST,
    instance_to_model_info,
    bridge_test_helper,
    make_request_with_user,
    FieldChecker,
)
from ..baker_recipes import (
    graph_anchor_recipe,
    tutorial_anchor_recipe,
    tag_anchor_recipe,
    graph_recipe,
    graph_description_recipe,
)
from ..data_bridge.graph_bridge import (
    GraphAnchorBridge,
    GraphBridge,
    GraphDescriptionBridge,
)
from ..models import (
    GraphOrder,
    UserRoles,
    User,
    GraphAnchor,
    TagAnchor,
    TutorialAnchor,
    OrderedAnchorTable,
    Graph,
    GraphDescription,
)
from ..types import (
    GraphAnchorMutationType,
    OrderedTutorialAnchorBindingType,
    TutorialAnchorMutationType,
    GraphMutationType,
    GraphDescriptionMutationType,
    UserMutationType,
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


@pytest.fixture
def graph_fixture(transactional_db):
    return graph_recipe.make()


@pytest.fixture
def graph_description_fixture(transactional_db):
    return graph_description_recipe.make()


class TutorialAnchorsChecker(
    FieldChecker[Sequence[OrderedTutorialAnchorBindingType], Sequence[TutorialAnchor]]
):
    def set_expected_value(self, expected_value) -> FieldChecker:
        self._expected_value = {
            ordered_anchor.tutorial_anchor.id: ordered_anchor
            for ordered_anchor in expected_value
        }
        return self

    def _check(self) -> bool:
        actual_ordered_anchors: Sequence[
            OrderedAnchorTable
        ] = OrderedAnchorTable.objects.filter(tutorial_anchor__in=self._actual_value)

        assert len(actual_ordered_anchors) == len(self._expected_value)

        for actual_ordered_anchor in actual_ordered_anchors:
            expected_ordered_anchor = self._expected_value.get(
                actual_ordered_anchor.tutorial_anchor.id, None
            )
            if expected_ordered_anchor is None:
                return False
            if expected_ordered_anchor.order != actual_ordered_anchor.order:
                return False

        return True


TUTORIAL_ANCHORS_CHECKER = TutorialAnchorsChecker("tutorial_anchors")


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
            tutorial_anchor=instance_to_model_info(
                tutorial_anchor, TutorialAnchorMutationType
            ),
            order=GraphOrder.LOW,  # this is the default value, maybe I should query OrderedGraphAnchor
        )
        for tutorial_anchor in graph_anchor.tutorial_anchors.all()
    ]

    new_model_infos = [
        GraphAnchorMutationType(
            id=old_model_info.id,
            url="new-anchor-url",
            anchor_name="new_anchor_name",
            default_order=GraphOrder.HIGH,
        ),
        GraphAnchorMutationType(
            id=old_model_info.id,
            url="new-anchor-url",
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
        ),
    ]

    request = make_request_with_user(rf, get_fixture)

    for new_model_info in new_model_infos:
        bridge_test_helper(
            GraphAnchorBridge,
            new_model_info,
            old_model_info,
            request=request,
            min_user_role=UserRoles.AUTHOR,
            custom_checker=(TUTORIAL_ANCHORS_CHECKER,),
        )


class JSONChecker(FieldChecker):
    def set_expected_value(
        self, expected_value: str | Dict | List | int | float
    ) -> FieldChecker:
        if isinstance(expected_value, str):
            self._expected_value = json.loads(expected_value)
        else:
            self._expected_value = expected_value

        return self


GRAPH_JSON_CHECKER = JSONChecker("graph_json")


@pytest.mark.parametrize("get_fixture", USER_LIST, indirect=True)
def test_graph(rf, graph_fixture: Graph, get_fixture: User):
    old_model_info: GraphMutationType = instance_to_model_info(
        graph_fixture, GraphMutationType
    )

    new_model_infos = [
        GraphMutationType(
            id=graph_fixture.id,
            graph_anchor=GraphAnchorMutationType(id=graph_fixture.graph_anchor.id),
        ),  # delete the model
        GraphMutationType(
            id=graph_fixture.id,
            graph_anchor=GraphAnchorMutationType(id=graph_fixture.graph_anchor.id),
            graph_json={},
            makers=[UserMutationType(id=get_fixture.id)],
        ),  # dict json
        GraphMutationType(
            id=graph_fixture.id,
            graph_anchor=GraphAnchorMutationType(id=graph_fixture.graph_anchor.id),
            graph_json="{}",
            makers=[UserMutationType(id=get_fixture.id)],
        ),  # str json
        GraphMutationType(id=graph_fixture.id),  # delete the model
    ]

    for new_model_info in new_model_infos:
        request = make_request_with_user(rf, get_fixture)
        bridge_test_helper(
            GraphBridge,
            new_model_info,
            old_model_info,
            request=request,
            min_user_role=UserRoles.AUTHOR,
            custom_checker=(GRAPH_JSON_CHECKER,),
        )


@pytest.mark.parametrize("get_fixture", USER_LIST, indirect=True)
def test_graph_description(
    rf, graph_description_fixture: GraphDescription, get_fixture: User
):
    old_model_info: GraphDescriptionMutationType = instance_to_model_info(
        graph_description_fixture, GraphDescriptionMutationType
    )

    new_model_infos = [
        GraphDescriptionMutationType(
            id=graph_description_fixture.id,
            graph_anchor=GraphAnchorMutationType(
                id=graph_description_fixture.graph_anchor.id
            ),
        ),
        GraphDescriptionMutationType(
            id=graph_description_fixture.id,
            graph_anchor=GraphAnchorMutationType(
                id=graph_description_fixture.graph_anchor.id
            ),
            title="new title",
            description_markdown="new description",
            authors=[UserMutationType(id=get_fixture.id)],
        ),
        GraphDescriptionMutationType(
            id=graph_description_fixture.id,
        ),  # delete the model
    ]

    for new_model_info in new_model_infos:
        request = make_request_with_user(rf, get_fixture)
        bridge_test_helper(
            GraphDescriptionBridge,
            new_model_info,
            old_model_info,
            request=request,
            min_user_role=UserRoles.TRANSLATOR,
        )
