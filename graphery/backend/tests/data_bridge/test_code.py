from __future__ import annotations

import pytest

from ...baker_recipes import code_recipe, tutorial_anchor_recipe
from ..utils import (
    instance_to_model_info,
    bridge_test_helper,
    make_request_with_user,
    USER_LIST,
    FieldChecker,
    ORIGINAL_TEST_CODE,
    BLACKED_TEST_CODE,
)
from ...data_bridge import black_format_str, CodeBridge
from ...models import UserRoles
from ...types import CodeMutationType, TutorialAnchorMutationType


@pytest.fixture
def code_fixture(transactional_db):
    return code_recipe.make()


@pytest.fixture
def tutorial_anchor_fixture(transactional_db):
    return tutorial_anchor_recipe.make()


class CodeChecker(FieldChecker):
    def set_expected_value(self, expected_value: str) -> FieldChecker:
        self._expected_value = black_format_str(expected_value)
        return self


CODE_CHECKER = CodeChecker(field_name="code")


@pytest.mark.parametrize("get_fixture", USER_LIST, indirect=True)
def test_code_bridge(rf, code_fixture, tutorial_anchor_fixture, get_fixture):
    old_model_info = instance_to_model_info(code_fixture, CodeMutationType)

    new_model_infos = [
        CodeMutationType(
            id=old_model_info.id,
            tutorial_anchor=TutorialAnchorMutationType(id=tutorial_anchor_fixture.id),
        ),
        CodeMutationType(
            id=old_model_info.id,
            name="another new name",
            code=ORIGINAL_TEST_CODE,
            tutorial_anchor=TutorialAnchorMutationType(id=tutorial_anchor_fixture.id),
        ),
        CodeMutationType(
            id=old_model_info.id,
            name="new name",
            code=BLACKED_TEST_CODE,
            tutorial_anchor=TutorialAnchorMutationType(id=tutorial_anchor_fixture.id),
        ),
    ]

    for new_model_info in new_model_infos:
        bridge_test_helper(
            CodeBridge,
            new_model_info,
            old_model_info,
            request=make_request_with_user(rf, get_fixture),
            min_edit_user_role=UserRoles.AUTHOR,
            custom_checker=(CODE_CHECKER,),
        )


@pytest.mark.parametrize("get_fixture", USER_LIST, indirect=True)
def test_delete_code_bridge(rf, code_fixture, get_fixture):
    bridge_test_helper(
        CodeBridge,
        CodeMutationType(id=code_fixture.id),
        request=make_request_with_user(rf, get_fixture),
        min_delete_user_role=UserRoles.EDITOR,
        is_deleting=True,
    )
