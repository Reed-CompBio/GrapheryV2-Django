from __future__ import annotations


import pytest

from .utils import MutationChecker
from ...baker_recipes import tag_anchor_recipe
from ...models import Tag
from ...types import OperationType

tag_mutation_string = """\
mutation MyMutation($op: OperationType!, $data: TagMutationType!) {
    __typename
    mutateTag(data: $data, op: $op) {
        id
        modifiedTime
        itemStatus
        langCode
        name
    }
}
"""


@pytest.fixture()
def tag_anchor():
    return tag_anchor_recipe.make()


@pytest.mark.django_db
def test_create_tag(rf, tag_anchor, author_user, session_middleware):
    MutationChecker(
        tag_mutation_string,
        rf,
        variables={
            "op": OperationType.CREATE.name,
            "data": {
                "tagAnchor": {"id": str(tag_anchor.id)},
                "name": "new tag name",
                "description": "new tag description",
            },
        },
        user=author_user,
        session_middleware=session_middleware,
        has_error=False,
        count_change=1,
        model_cls=Tag,
        equals={
            "name": "new tag name",
            "description": "new tag description",
        },
    ).set_new_instance(Tag.objects.get(tag_anchor__id=tag_anchor.id)).check()


@pytest.mark.django_db
def test_create_tag_permission_fail(rf, tag_anchor, reader_user, session_middleware):
    MutationChecker(
        tag_mutation_string,
        rf,
        variables={
            "op": OperationType.CREATE.name,
            "data": {
                "tagAnchor": {"id": str(tag_anchor.id)},
                "name": "new tag name",
                "description": "new tag description",
            },
        },
        user=reader_user,
        session_middleware=session_middleware,
        model_cls=Tag,
        has_error=True,
        count_change=0,
    ).check()
