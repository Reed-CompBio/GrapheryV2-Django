from __future__ import annotations

import pytest

from .utils import USER_LIST, bridge_test_helper, instance_to_model_info
from ..baker_recipes import (
    tutorial_anchor_recipe,
    tag_anchor_recipe,
    tutorial_recipe,
    user_recipe,
)
from ..data_bridge import TutorialAnchorBridge, TutorialBridge, ValidationError
from ..models import User, UserRoles, Status
from ..types import (
    TutorialAnchorMutationType,
    TagAnchorMutationType,
    TutorialMutationType,
    UserMutationType,
)


@pytest.fixture(scope="function")
def tag_anchors(transactional_db):
    tag_anchors = tag_anchor_recipe.make(_quantity=5)
    return tag_anchors


@pytest.fixture(scope="function")
def tutorial_anchor(transactional_db, tag_anchors):
    tutorial_anchor = tutorial_anchor_recipe.make(tag_anchors=tag_anchors)
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
