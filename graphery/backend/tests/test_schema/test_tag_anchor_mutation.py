from __future__ import annotations

from operator import gt

import pytest

from .utils import MutationChecker
from ...baker_recipes import tag_anchor_recipe
from ...models import TagAnchor, Status
from ...types import OperationType

tag_anchor_mutation_string = """
    mutation MyMutation($op: OperationType!, $data: TagAnchorMutationType!) {
        mutateTagAnchor(op: $op, data: $data) {
            id
            anchorName
            modifiedTime
            itemStatus
        }
    }
"""


@pytest.mark.django_db
def test_create_tag_anchor(rf, editor_user, session_middleware):
    checker = (
        MutationChecker(
            tag_anchor_mutation_string,
            rf,
            variables={
                "op": OperationType.CREATE.name,
                "data": {
                    "itemStatus": Status.REVIEWING.name,
                    "anchorName": "test tag creation",
                },
            },
            user=editor_user,
            model_cls=TagAnchor,
            has_error=False,
            count_change=1,
            session_middleware=session_middleware,
            equals={
                "anchor_name": "test tag creation",
                "item_status": Status.REVIEWING,
            },
        )
        .set_new_instance(TagAnchor.objects.get(anchor_name="test tag creation"))
        .check()
    )

    assert str(checker.new_instance.id) == checker.result.data["mutateTagAnchor"]["id"]


@pytest.mark.django_db
def test_create_tag_anchor_permission_fail(rf, reader_user, session_middleware):
    checker = MutationChecker(
        tag_anchor_mutation_string,
        rf,
        variables={
            "op": OperationType.CREATE.name,
            "data": {
                "itemStatus": Status.REVIEWING.name,
                "anchorName": "test tag creation",
            },
        },
        user=reader_user,
        model_cls=TagAnchor,
        has_error=True,
        count_change=0,
        session_middleware=session_middleware,
    ).check()

    assert checker.result.errors[0].message.find("You do not have the permission") > -1


@pytest.mark.skip(reason="not implemented yet")
@pytest.mark.django_db
def test_create_tag_anchor_constraint_fail(rf, editor_user, session_middleware):
    MutationChecker(
        tag_anchor_mutation_string,
        rf,
        variables={
            "op": OperationType.CREATE.name,
            "data": {},
        },
        user=editor_user,
        session_middleware=session_middleware,
        has_error=True,
        count_change=0,
        model_cls=TagAnchor,
    ).check()


@pytest.fixture()
def tag_anchor():
    return tag_anchor_recipe.make(
        anchor_name="old anchor name", item_status=Status.DRAFT
    )


@pytest.mark.django_db
def test_update_tag_anchor(rf, editor_user, tag_anchor, session_middleware):
    MutationChecker(
        tag_anchor_mutation_string,
        rf,
        variables={
            "op": OperationType.UPDATE.name,
            "data": {
                "id": str(tag_anchor.id),
                "anchorName": "new anchor name",
                "itemStatus": Status.REVIEWING.name,
            },
        },
        user=editor_user,
        session_middleware=session_middleware,
        has_error=False,
        count_change=0,
        model_cls=TagAnchor,
        old_instance=tag_anchor,
        equals={"anchor_name": "new anchor name", "item_status": Status.REVIEWING},
        diff={"anchor_name", "modified_time", "item_status"},
        compare={"modified_time": gt},
    ).set_new_instance().check()


@pytest.mark.django_db
def test_update_tag_anchor_permission_fail(
    rf, reader_user, tag_anchor, session_middleware
):
    MutationChecker(
        tag_anchor_mutation_string,
        rf,
        variables={
            "op": OperationType.UPDATE.name,
            "data": {
                "id": str(tag_anchor.id),
                "anchorName": "new anchor name",
                "itemStatus": Status.REVIEWING.name,
            },
        },
        user=reader_user,
        session_middleware=session_middleware,
        has_error=True,
        count_change=0,
        model_cls=TagAnchor,
        old_instance=tag_anchor,
        not_equals={"anchor_name": "new anchor name", "item_status": Status.REVIEWING},
        same={"anchor_name", "modified_time", "item_status"},
    ).set_new_instance().check()


@pytest.mark.djago_db
def test_delete_tag_anchor(rf, admin_user, tag_anchor, session_middleware):
    MutationChecker(
        tag_anchor_mutation_string,
        rf,
        variables={
            "op": OperationType.DELETE.name,
            "data": {"id": str(tag_anchor.id)},
        },
        user=admin_user,
        session_middleware=session_middleware,
        has_error=False,
        count_change=-1,
        model_cls=TagAnchor,
    ).check()


@pytest.mark.djago_db
def test_delete_tag_anchor_permission_fail(
    rf, author_user, tag_anchor, session_middleware
):
    MutationChecker(
        tag_anchor_mutation_string,
        rf,
        variables={
            "op": OperationType.DELETE.name,
            "data": {"id": str(tag_anchor.id)},
        },
        user=author_user,
        session_middleware=session_middleware,
        has_error=True,
        count_change=0,
        model_cls=TagAnchor,
    ).check()
