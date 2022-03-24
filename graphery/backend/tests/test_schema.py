from __future__ import annotations

from asgiref.sync import sync_to_async

from typing import List

import pytest

from ..baker_recipes import tag_anchor_recipe
from ..models import TagAnchor
from ..schema import schema


@pytest.mark.django_db
def make_tag_anchors(quantity: int = 3) -> List[TagAnchor]:
    three_tag_anchors = tag_anchor_recipe.make(_quantity=quantity)
    return three_tag_anchors


@pytest.mark.django_db
def test_get_all_tag_anchors(rf):
    query = """\
        query TagAnchorQuery {
            __typename
            tagAnchors {
                id
                itemStatus
                modifiedTime
                createdTime
                anchorName
            }
        }
    """
    tag_anchors = make_tag_anchors()

    response = schema.execute_sync(query)

    assert response.errors is None
    assert len(response.data["tagAnchors"]) == len(tag_anchors)
    response_ids = list(map(lambda x: x["id"], response.data["tagAnchors"]))
    target_ids = list(map(lambda x: str(x.id), tag_anchors))
    assert all(ident in response_ids for ident in target_ids)
