from __future__ import annotations

import pytest

from .utils import USER_LIST, bridge_test_helper, instance_to_model_info
from ..baker_recipes import tutorial_anchor_recipe, tag_anchor_recipe
from ..data_bridge import TutorialAnchorBridge
from ..models import User, UserRoles, Status
from ..types import TutorialAnchorMutationType, TagAnchorMutationType


@pytest.fixture(scope="function")
def tag_anchors(transactional_db):
    tag_anchors = tag_anchor_recipe.make(_quantity=5)
    return tag_anchors


@pytest.fixture(scope="function")
def tutorial_anchor(transactional_db, tag_anchors):
    tutorial_anchor = tutorial_anchor_recipe.make(tag_anchors=tag_anchors)
    return tutorial_anchor


@pytest.mark.parametrize(
    "get_fixture",
    USER_LIST,
    indirect=True,
)
def test_tutorial_anchor(rf, tutorial_anchor, tag_anchors, get_fixture: User):
    model_infos = [
        TutorialAnchorMutationType(
            id=tutorial_anchor.id,
            url="new_url",
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
        ),
    ]
    old_model_info = instance_to_model_info(tutorial_anchor, TutorialAnchorMutationType)

    for model_info in model_infos:
        request = rf.post("/graphql/sync")
        request.user = get_fixture

        bridge_test_helper(
            TutorialAnchorBridge, model_info, old_model_info, request, UserRoles.AUTHOR
        )
