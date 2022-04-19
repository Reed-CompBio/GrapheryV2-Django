from __future__ import annotations

import pytest

from ..utils import (
    USER_LIST,
    instance_to_model_info,
    bridge_test_helper,
    make_request_with_user,
    JSONChecker,
)
from ...baker_recipes import execution_result_recipe, code_recipe, graph_anchor_recipe
from ...data_bridge import ExecutionResultBridge
from ...models import UserRoles
from ...types import (
    ExecutionResultMutationType,
    CodeMutationType,
    GraphAnchorMutationType,
)


@pytest.fixture
def code_fixture(transactional_db):
    return code_recipe.make()


@pytest.fixture
def graph_anchor_fixture(transactional_db):
    return graph_anchor_recipe.make()


@pytest.fixture
def execution_result_fixture(transactional_db, code_fixture):
    return execution_result_recipe.make(code=code_fixture)


@pytest.fixture
def execution_model_info(request, execution_result_fixture):
    params = {
        param: fn(execution_result_fixture) for param, fn in request.param.items()
    }

    return ExecutionResultMutationType(
        id=execution_result_fixture.id,
        result_json='{"1": 1, "2": 2}',
        **params,
    )


EXECUTION_RESULT_JSON_CHECKER = JSONChecker(field_name="result_json")
EXECUTION_META_JSON_CHECKER = JSONChecker(field_name="result_json_meta")


@pytest.mark.parametrize(
    "get_fixture, execution_model_info",
    [
        (user, model_param)
        for user in USER_LIST
        for model_param in [
            {
                "code": lambda exe: CodeMutationType(id=exe.code.id),
                "graph_anchor": lambda exe: GraphAnchorMutationType(
                    id=exe.graph_anchor.id
                ),
            },
            {
                "graph_anchor": lambda exe: GraphAnchorMutationType(
                    id=exe.graph_anchor.id
                )
            },
            {
                "code": lambda exe: CodeMutationType(id=exe.code.id),
            },
            {},
        ]
    ],
    indirect=True,
)
def test_execution_result(
    rf, get_fixture, execution_model_info, execution_result_fixture
):
    old_model_info = instance_to_model_info(
        execution_result_fixture, ExecutionResultMutationType
    )

    bridge_test_helper(
        ExecutionResultBridge,
        execution_model_info,
        old_model_info,
        request=make_request_with_user(rf, get_fixture),
        min_user_role=UserRoles.AUTHOR,
        custom_checker=(EXECUTION_RESULT_JSON_CHECKER, EXECUTION_META_JSON_CHECKER),
    )
