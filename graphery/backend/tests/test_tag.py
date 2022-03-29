from __future__ import annotations

import pytest

from ..baker_recipes import tag_anchor_recipe
from ..data_bridge import TagAnchorBridge
from ..models import Status, User, UserRoles, TagAnchor
from ..types import TagAnchorMutationType


@pytest.fixture(scope="function")
def tag_anchor(transactional_db):
    tag_anchor = tag_anchor_recipe.make(
        item_status=Status.AUTOSAVE, anchor_name="old anchor name"
    )
    return tag_anchor


@pytest.mark.parametrize(
    "get_fixture",
    ["admin_user", "editor_user", "author_user", "visitor_user", "reader_user"],
    indirect=True,
)
def test_tag_anchor(rf, tag_anchor, get_fixture: User):
    model_info = TagAnchorMutationType(
        id=tag_anchor.id,
        item_status=Status.PUBLISHED,
        anchor_name="new anchor name",
    )

    request = rf.post("/graphql", data=None, content_type="application/json")

    # admin user can update
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
