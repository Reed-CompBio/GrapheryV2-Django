from __future__ import annotations

from typing import Sequence

import pytest

from .utils import (
    USER_LIST,
    bridge_test_helper,
    instance_to_model_info,
    make_request_with_user,
    FieldChecker,
)
from ..baker_recipes import (
    tutorial_anchor_recipe,
    tag_anchor_recipe,
    tutorial_recipe,
    user_recipe,
    graph_anchor_recipe,
)
from ..data_bridge import TutorialAnchorBridge, TutorialBridge, ValidationError
from ..models import (
    User,
    UserRoles,
    Status,
    GraphOrder,
    GraphAnchor,
    OrderedGraphAnchor,
)
from ..types import (
    TutorialAnchorMutationType,
    TagAnchorMutationType,
    TutorialMutationType,
    UserMutationType,
    OrderedGraphAnchorBindingType,
    GraphAnchorMutationType,
)


@pytest.fixture(scope="function")
def tag_anchors(transactional_db):
    tag_anchors = tag_anchor_recipe.make(_quantity=5)
    return tag_anchors


@pytest.fixture(scope="function")
def tutorial_anchor(transactional_db, tag_anchors):
    tutorial_anchor = tutorial_anchor_recipe.make(
        tag_anchors=tag_anchors, graph_anchors=graph_anchor_recipe.make(_quantity=3)
    )
    return tutorial_anchor


@pytest.fixture(scope="function")
def author_users(transactional_db):
    return user_recipe.make(_quantity=5, role=UserRoles.AUTHOR)


@pytest.fixture(scope="function")
def invalid_users(transactional_db):
    return user_recipe.make(_quantity=2, role=UserRoles.READER)


@pytest.fixture(scope="function")
def tutorial(transactional_db, tutorial_anchor, author_users):
    tutorial = tutorial_recipe.make(
        tutorial_anchor=tutorial_anchor, authors=author_users
    )
    return tutorial


@pytest.fixture(scope="function")
def graph_anchors(transactional_db):
    graph_anchors = graph_anchor_recipe.make(_quantity=5)

    return graph_anchors


class GraphAnchorsChecker(
    FieldChecker[Sequence[OrderedGraphAnchorBindingType], Sequence[GraphAnchor]]
):
    def set_expected_value(self, expected_value) -> FieldChecker:
        self._expected_value = {
            ordered_anchor.graph_anchor.id: ordered_anchor
            for ordered_anchor in expected_value
        }
        return self

    def _check(self) -> bool:
        actual_ordered_anchors: Sequence[
            OrderedGraphAnchor
        ] = OrderedGraphAnchor.objects.filter(graph_anchor__in=self._actual_value)

        assert len(actual_ordered_anchors) == len(self._expected_value)

        for actual_ordered_anchor in actual_ordered_anchors:
            expected_ordered_anchor = self._expected_value.get(
                actual_ordered_anchor.graph_anchor.id, None
            )
            if expected_ordered_anchor is None:
                return False
            if expected_ordered_anchor.order != actual_ordered_anchor.order:
                return False

        return True


GRAPH_ANCHOR_CHECKER = GraphAnchorsChecker("graph_anchors")


@pytest.mark.parametrize(
    "get_fixture",
    USER_LIST,
    indirect=True,
)
def test_tutorial_anchor(
    rf, tutorial_anchor, tag_anchors, get_fixture: User, graph_anchors
):
    model_infos = [
        TutorialAnchorMutationType(
            id=tutorial_anchor.id,
            url="new-anchor-url",
            anchor_name="new anchor name",
            item_status=Status.PUBLISHED,
        ),
        TutorialAnchorMutationType(
            id=tutorial_anchor.id,
            url="new_url",
            anchor_name="new anchor name",
            item_status=Status.PUBLISHED,
            tag_anchors=[
                TagAnchorMutationType(id=tag_anchor.id)
                for tag_anchor in tag_anchors[:3]
            ],
            graph_anchors=[
                OrderedGraphAnchorBindingType(
                    graph_anchor=instance_to_model_info(
                        graph_anchor, GraphAnchorMutationType
                    ),
                    order=GraphOrder.HIGH,
                )
                for graph_anchor in graph_anchors
            ],
        ),
    ]

    old_model_info = instance_to_model_info(
        tutorial_anchor, TutorialAnchorMutationType, ignore_value="graph_anchors"
    )
    old_model_info.graph_anchors = [
        OrderedGraphAnchorBindingType(
            graph_anchor=instance_to_model_info(graph_anchor, GraphAnchorMutationType),
            order=GraphOrder.HIGH,
        )
        for graph_anchor in tutorial_anchor.graph_anchors.all()
    ]

    for model_info in model_infos:
        request = make_request_with_user(rf, get_fixture)

        bridge_test_helper(
            TutorialAnchorBridge,
            model_info,
            old_model_info,
            request,
            UserRoles.AUTHOR,
            custom_checker=(GRAPH_ANCHOR_CHECKER,),
        )


@pytest.mark.parametrize(
    "get_fixture",
    USER_LIST,
    indirect=True,
)
def test_tutorial(rf, tutorial, author_users, get_fixture: User):
    model_infos = [
        TutorialMutationType(
            id=tutorial.id,
            tutorial_anchor=TutorialAnchorMutationType(id=tutorial.tutorial_anchor.id),
            authors=[UserMutationType(id=author.id) for author in author_users[:3]],
            title="new title",
            abstract="new abstract",
            content_markdown="new content",
        ),
        TutorialMutationType(
            id=tutorial.id,
            authors=[UserMutationType(id=author.id) for author in author_users[:3]],
            title="new title",
            abstract="new abstract",
            content_markdown="new content",
        ),
    ]
    old_model_info = instance_to_model_info(tutorial, TutorialMutationType)

    for model_info in model_infos:
        request = rf.post("/graphql/sync")
        request.user = get_fixture

        bridge_test_helper(
            TutorialBridge, model_info, old_model_info, request, UserRoles.TRANSLATOR
        )


def test_tutorial_author_assignment(rf, tutorial, invalid_users, translator_user):
    model_info = TutorialMutationType(
        id=tutorial.id,
        tutorial_anchor=TutorialAnchorMutationType(id=tutorial.tutorial_anchor.id),
        authors=[UserMutationType(id=user.id) for user in invalid_users],
    )
    old_model_info = instance_to_model_info(tutorial, TutorialMutationType)

    request = rf.post("/graphql/sync")
    request.user = translator_user

    with pytest.raises(ValidationError):
        bridge_test_helper(
            TutorialBridge, model_info, old_model_info, request, UserRoles.TRANSLATOR
        )
