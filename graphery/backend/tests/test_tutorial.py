from __future__ import annotations

import pytest
from strawberry.arguments import UNSET

from .utils import USER_LIST
from ..baker_recipes import tutorial_anchor_recipe, tag_anchor_recipe
from ..data_bridge import TutorialAnchorBridge
from ..models import User, UserRoles, TutorialAnchor, Status
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

    for model_info in model_infos:
        request = rf.post("/graphql/sync")
        request.user = get_fixture

        if get_fixture.role < UserRoles.AUTHOR:
            with pytest.raises(Exception):
                TutorialAnchorBridge.bridges_from_model_info(
                    model_info, request=request
                )
            tutorial_anchor = TutorialAnchor.objects.get(id=tutorial_anchor.id)
        else:
            TutorialAnchorBridge.bridges_from_model_info(model_info, request=request)
            try:
                tutorial_anchor = TutorialAnchor.objects.get(id=model_info.id)
            except TutorialAnchor.DoesNotExist:
                assert (
                    model_info.tag_anchor is UNSET
                ), "tutorial_anchor is empty, but Tutorial still exists"
            else:
                assert tutorial_anchor.url == model_info.url
                assert tutorial_anchor.item_status == model_info.item_status
                assert tutorial_anchor.anchor_name == model_info.anchor_name
                if model_info.tag_anchors is UNSET:
                    assert tutorial_anchor.tag_anchors.count() == len(tag_anchors)
                else:
                    assert tutorial_anchor.tag_anchors.count() == len(
                        model_info.tag_anchors
                    )
