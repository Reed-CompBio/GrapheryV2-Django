from __future__ import annotations

import pytest

from ..utils import (
    USER_LIST,
    bridge_test_helper,
    instance_to_model_info,
    make_request_with_user,
)
from ...baker_recipes import tag_anchor_recipe, tag_recipe
from ...data_bridge import TagAnchorBridge, TagBridge
from ...models import Status, User, UserRoles
from ...types import TagAnchorMutationType, TagMutationType


@pytest.fixture(scope="function")
def tag_anchor(transactional_db):
    tag_anchor = tag_anchor_recipe.make(
        item_status=Status.AUTOSAVE, anchor_name="old anchor name"
    )
    return tag_anchor


@pytest.fixture(scope="function")
def tag(transactional_db, tag_anchor):
    tag = tag_recipe.make(
        item_status=Status.DRAFT,
        name="Old Tag Name",
        tag_anchor=tag_anchor,
        description="Old Tag Description",
    )
    return tag


@pytest.mark.parametrize(
    "get_fixture",
    USER_LIST,
    indirect=True,
)
def test_tag_anchor(rf, tag_anchor, get_fixture: User):
    new_model_info = TagAnchorMutationType(
        id=tag_anchor.id,
        item_status=Status.PUBLISHED,
        anchor_name="new anchor name",
    )
    old_model_info = instance_to_model_info(tag_anchor, TagAnchorMutationType)

    request = rf.post("/graphql", data=None, content_type="application/json")
    # privileged user can update
    request.user = get_fixture

    bridge_test_helper(
        TagAnchorBridge, new_model_info, old_model_info, request, UserRoles.AUTHOR
    )


@pytest.mark.parametrize(
    "get_fixture",
    USER_LIST,
    indirect=True,
)
def test_tag(rf, tag, get_fixture: User):
    model_infos = [
        TagMutationType(
            id=tag.id,
            item_status=Status.PUBLISHED,
            name="New Tag Name",
            description="New Tag Description",
            tag_anchor=TagAnchorMutationType(id=tag.tag_anchor.id),
        ),
    ]
    old_model_info = instance_to_model_info(tag, TagMutationType)

    for model_info in model_infos:
        request = make_request_with_user(rf, get_fixture)
        bridge_test_helper(
            TagBridge, model_info, old_model_info, request, UserRoles.AUTHOR
        )


@pytest.mark.parametrize("get_fixture", USER_LIST, indirect=True)
def test_delete_tag(rf, tag, get_fixture):
    new_info = TagMutationType(
        id=tag.id,
        item_status=Status.PUBLISHED,
        name="New Tag Name",
        description="New Tag Description",
    )

    bridge_test_helper(
        TagBridge,
        new_info,
        min_delete_user_role=UserRoles.EDITOR,
        is_deleting=True,
        request=make_request_with_user(rf, get_fixture),
    )
