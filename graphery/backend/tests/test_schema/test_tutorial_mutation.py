from __future__ import annotations


import pytest

from ...baker_recipes import tutorial_anchor_recipe
from .utils import MutationChecker
from ...models import Tutorial, Status, LangCode
from ...types import OperationType


@pytest.fixture()
def tutorial_anchor():
    return tutorial_anchor_recipe.make(url="test-url")


tutorial_mutation_string = """\
mutation MyMutation($op: OperationType!, $data:TutorialMutationType!) {
  __typename
  mutateTutorial(data: $data, op: $op) {
    id
    modifiedTime
    itemStatus
    title
    langCode
    contentMarkdown
    abstract
  }
}
"""


@pytest.mark.django_db
def test_create_tutorial_prevented(
    rf, session_middleware, author_user, tutorial_anchor
):
    MutationChecker(
        tutorial_mutation_string,
        rf,
        variables={
            "op": OperationType.CREATE.name,
            "data": {
                "tutorialAnchor": {"id": str(tutorial_anchor.id)},
                "title": "new tutorial title",
                "description": "new tutorial description",
                "status": Status.REVIEWING.name,
            },
        },
        user=author_user,
        session_middleware=session_middleware,
        has_error=True,
        count_change=0,
        model_cls=Tutorial,
    ).check()


@pytest.mark.django_db
def test_add_tutorial(rf, session_middleware, author_user, tutorial_anchor):
    MutationChecker(
        tutorial_mutation_string,
        rf,
        variables={
            "op": OperationType.UPDATE.name,
            "data": {
                "tutorialAnchor": {"id": str(tutorial_anchor.id)},
                "title": "new tutorial title",
                "abstract": "new tutorial description",
                "contentMarkdown": "# new tutorial content",
                "itemStatus": Status.AUTOSAVE.name,
                "langCode": LangCode.EN.name,
            },
        },
        user=author_user,
        session_middleware=session_middleware,
        has_error=False,
        count_change=1,
        model_cls=Tutorial,
        equals={
            "title": "new tutorial title",
            "abstract": "new tutorial description",
            "content_markdown": "# new tutorial content",
            "item_status": Status.AUTOSAVE,
            "lang_code": LangCode.EN,
            "tutorial_anchor": tutorial_anchor,
        },
    ).set_new_instance(Tutorial.objects.get(title="new tutorial title")).check()


@pytest.mark.django_db
def test_append_tutorial(rf, session_middleware, author_user, tutorial_anchor):
    first_checker = (
        MutationChecker(
            tutorial_mutation_string,
            rf,
            variables={
                "op": OperationType.UPDATE.name,
                "data": {
                    "tutorialAnchor": {"id": str(tutorial_anchor.id)},
                    "title": "new tutorial title",
                    "abstract": "new tutorial description",
                    "contentMarkdown": "# new tutorial content",
                    "itemStatus": Status.AUTOSAVE.name,
                    "langCode": LangCode.EN.name,
                },
            },
            user=author_user,
            session_middleware=session_middleware,
            has_error=False,
            count_change=1,
            model_cls=Tutorial,
            equals={
                "tutorial_anchor": tutorial_anchor,
            },
        )
        .set_new_instance(Tutorial.objects.get(title="new tutorial title"))
        .check()
    )

    MutationChecker(
        tutorial_mutation_string,
        rf,
        variables={
            "op": OperationType.UPDATE.name,
            "data": {
                "tutorialAnchor": {"id": str(tutorial_anchor.id)},
                "title": "new tutorial title",
                "abstract": "new tutorial description 2",
                "contentMarkdown": "# new tutorial content 2",
                "itemStatus": Status.DRAFT.name,
                "langCode": LangCode.EN.name,
            },
        },
        user=author_user,
        session_middleware=session_middleware,
        has_error=False,
        count_change=1,
        model_cls=Tutorial,
        equals={
            "title": "new tutorial title",
            "abstract": "new tutorial description 2",
            "content_markdown": "# new tutorial content 2",
            "item_status": Status.DRAFT,
            "lang_code": LangCode.EN,
            "back": first_checker.new_instance,
        },
    ).set_new_instance(
        Tutorial.objects.get(abstract="new tutorial description 2")
    ).check()


@pytest.mark.django_db
def test_replacing_tutorial(rf, session_middleware, editor_user, tutorial_anchor):
    first_check = (
        MutationChecker(
            tutorial_mutation_string,
            rf,
            variables={
                "op": OperationType.UPDATE.name,
                "data": {
                    "tutorialAnchor": {"id": str(tutorial_anchor.id)},
                    "title": "new tutorial title",
                    "abstract": "new tutorial description",
                    "contentMarkdown": "# new tutorial content",
                    "itemStatus": Status.AUTOSAVE.name,
                    "langCode": LangCode.EN.name,
                },
            },
            user=editor_user,
            session_middleware=session_middleware,
            has_error=False,
            count_change=1,
            model_cls=Tutorial,
        )
        .set_new_instance(Tutorial.objects.get(tutorial_anchor=tutorial_anchor))
        .check()
    )

    second_check = (
        MutationChecker(
            tutorial_mutation_string,
            rf,
            variables={
                "op": OperationType.UPDATE.name,
                "data": {
                    "tutorialAnchor": {"id": str(tutorial_anchor.id)},
                    "title": "new tutorial title",
                    "abstract": "new tutorial description 2",
                    "contentMarkdown": "# new tutorial content 2",
                    "itemStatus": Status.REVIEWING.name,
                    "langCode": LangCode.EN.name,
                },
            },
            user=editor_user,
            session_middleware=session_middleware,
            has_error=False,
            count_change=0,
            model_cls=Tutorial,
            equals={
                "back": None,
                "title": "new tutorial title",
                "abstract": "new tutorial description 2",
                "content_markdown": "# new tutorial content 2",
                "item_status": Status.REVIEWING,
                "lang_code": LangCode.EN,
            },
        )
        .set_new_instance(Tutorial.objects.get(tutorial_anchor=tutorial_anchor))
        .check()
    )

    third_check = (
        MutationChecker(
            tutorial_mutation_string,
            rf,
            variables={
                "op": OperationType.UPDATE.name,
                "data": {
                    "tutorialAnchor": {"id": str(tutorial_anchor.id)},
                    "title": "new tutorial title",
                    "abstract": "new tutorial description 3",
                    "contentMarkdown": "# new tutorial content 3",
                    "itemStatus": Status.PUBLISHED.name,
                    "langCode": LangCode.EN.name,
                },
            },
            user=editor_user,
            session_middleware=session_middleware,
            has_error=False,
            count_change=0,
            model_cls=Tutorial,
            equals={
                "back": None,
                "title": "new tutorial title",
                "abstract": "new tutorial description 3",
                "content_markdown": "# new tutorial content 3",
                "item_status": Status.PUBLISHED,
                "lang_code": LangCode.EN,
            },
        )
        .set_new_instance(Tutorial.objects.get(tutorial_anchor=tutorial_anchor))
        .check()
    )

    third_check = (
        MutationChecker(
            tutorial_mutation_string,
            rf,
            variables={
                "op": OperationType.UPDATE.name,
                "data": {
                    "tutorialAnchor": {"id": str(tutorial_anchor.id)},
                    "title": "new tutorial title",
                    "abstract": "new tutorial description 4",
                    "contentMarkdown": "# new tutorial content 4",
                    "itemStatus": Status.AUTOSAVE.name,
                    "langCode": LangCode.EN.name,
                },
            },
            user=editor_user,
            session_middleware=session_middleware,
            has_error=False,
            count_change=1,
            model_cls=Tutorial,
            equals={
                "back": third_check.new_instance,
                "title": "new tutorial title",
                "abstract": "new tutorial description 4",
                "content_markdown": "# new tutorial content 4",
                "item_status": Status.AUTOSAVE,
                "lang_code": LangCode.EN,
            },
        )
        .set_new_instance(Tutorial.objects.get(item_status=Status.AUTOSAVE))
        .check()
    )


def test_closing_tutorial(rf, session_middleware, editor_user, tutorial_anchor):
    first_check = (
        MutationChecker(
            tutorial_mutation_string,
            rf,
            variables={
                "op": OperationType.UPDATE.name,
                "data": {
                    "tutorialAnchor": {"id": str(tutorial_anchor.id)},
                    "title": "new tutorial title",
                    "abstract": "new tutorial description",
                    "contentMarkdown": "# new tutorial content",
                    "itemStatus": Status.PUBLISHED.name,
                    "langCode": LangCode.EN.name,
                },
            },
            user=editor_user,
            session_middleware=session_middleware,
            has_error=False,
            count_change=1,
            model_cls=Tutorial,
        )
        .set_new_instance(Tutorial.objects.get(tutorial_anchor=tutorial_anchor))
        .check()
    )

    second_check = (
        MutationChecker(
            tutorial_mutation_string,
            rf,
            variables={
                "op": OperationType.UPDATE.name,
                "data": {
                    "tutorialAnchor": {"id": str(tutorial_anchor.id)},
                    "title": "new tutorial title",
                    "abstract": "new tutorial description 2",
                    "contentMarkdown": "# new tutorial content 2",
                    "itemStatus": Status.REVIEWING.name,
                    "langCode": LangCode.EN.name,
                },
            },
            user=editor_user,
            session_middleware=session_middleware,
            has_error=False,
            count_change=1,
            model_cls=Tutorial,
            equals={
                "back": first_check.new_instance,
                "title": "new tutorial title",
                "abstract": "new tutorial description 2",
                "content_markdown": "# new tutorial content 2",
                "item_status": Status.REVIEWING,
                "lang_code": LangCode.EN,
            },
        )
        .set_new_instance(Tutorial.objects.get(item_status=Status.REVIEWING))
        .check()
    )

    third_check = (
        MutationChecker(
            tutorial_mutation_string,
            rf,
            variables={
                "op": OperationType.UPDATE.name,
                "data": {
                    "tutorialAnchor": {"id": str(tutorial_anchor.id)},
                    "title": "new tutorial title",
                    "abstract": "new tutorial description 3",
                    "contentMarkdown": "# new tutorial content 3",
                    "itemStatus": Status.PUBLISHED.name,
                    "langCode": LangCode.EN.name,
                },
            },
            user=editor_user,
            session_middleware=session_middleware,
            has_error=False,
            count_change=0,
            model_cls=Tutorial,
            equals={
                "back": first_check.new_instance,
                "title": "new tutorial title",
                "abstract": "new tutorial description 3",
                "content_markdown": "# new tutorial content 3",
                "item_status": Status.PUBLISHED,
                "lang_code": LangCode.EN,
            },
        )
        .set_new_instance(Tutorial.objects.get(item_status=Status.PUBLISHED))
        .check()
    )

    assert (
        third_check.new_instance.back.item_status == Status.CLOSED
    ), "Tutorial should be closed"
