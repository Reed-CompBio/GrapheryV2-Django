from __future__ import annotations

import executor
import pytest

from ...baker_recipes.make_test_examples import DEFAULT_GRAPH_JSON, DEFAULT_CODE_CONTENT
from .utils import MutationChecker


executor_mutation = """\
mutation ($code:String!, $graph:String!, $version:String!, $options:RequestOptionType){
  __typename
  executionRequest(request: {code: $code, graph: $graph, version: $version, options: $options}) {
    info {
      result
    }
    errors {
      message
      traceback
    }
  }
}
"""


@pytest.mark.django_db
def test_executor_mutation(rf, session_middleware, reader_user):
    checker = MutationChecker(
        executor_mutation,
        rf,
        user=reader_user,
        variables={
            "code": DEFAULT_CODE_CONTENT,
            "graph": DEFAULT_GRAPH_JSON,
            "version": executor.SERVER_VERSION,
            "options": {
                "randSeed": 32,
                "floatPrecision": 10,
                "inputList": ["a", "b", "c"],
            },
        },
        session_middleware=session_middleware,
        has_error=False,
    ).check()

    assert checker.result.data["executionRequest"]["errors"] is None
