from __future__ import annotations

import pytest
from strawberry.arguments import UNSET

from .utils import USER_LIST
from ..baker_recipes import tag_anchor_recipe, tag_recipe
from ..data_bridge import TagAnchorBridge, TagBridge
from ..models import Status, User, UserRoles, TagAnchor, Tag
from ..types import TagAnchorMutationType, TagMutationType


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
    model_info = TagAnchorMutationType(
        id=tag_anchor.id,
        item_status=Status.PUBLISHED,
        anchor_name="new anchor name",
    )

    request = rf.post("/graphql", data=None, content_type="application/json")

    # privileged user can update
    request.user = get_fixture
    if get_fixture.role <= UserRoles.VISITOR:
        with pytest.raises(Exception):
            TagAnchorBridge.bridges_from_model_info(model_info, request=request)
        tag_anchor = TagAnchor.objects.get(id=model_info.id)
        assert tag_anchor.anchor_name == "old anchor name"
        assert tag_anchor.item_status == Status.AUTOSAVE
    else:
        TagAnchorBridge.bridges_from_model_info(model_info, request=request)
        tag_anchor = TagAnchor.objects.get(id=model_info.id)
        assert tag_anchor.anchor_name == model_info.anchor_name
        assert tag_anchor.item_status == model_info.item_status


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
        TagMutationType(
            id=tag.id,
            item_status=Status.PUBLISHED,
            name="New Tag Name",
            description="New Tag Description",
        ),
    ]

    for model_info in model_infos:
        request = rf.post("/graphql", data=None, content_type="application/json")

        # privileged user can update
        request.user = get_fixture
        if get_fixture.role <= UserRoles.VISITOR:
            with pytest.raises(Exception):
                TagBridge.bridges_from_model_info(model_info, request=request)
            tag = Tag.objects.get(id=model_info.id)
            assert tag.name == "Old Tag Name"
            assert tag.item_status == Status.DRAFT
            assert tag.description == "Old Tag Description"
        else:
            TagBridge.bridges_from_model_info(model_info, request=request)
            try:
                tag = Tag.objects.get(id=model_info.id)
            except Tag.DoesNotExist:
                if model_info.tag_anchor is not UNSET:
                    assert False, "TagAnchor is empty, but Tag still exists"
            else:
                assert tag.name == model_info.name
                assert tag.item_status == model_info.item_status
                assert tag.description == model_info.description
