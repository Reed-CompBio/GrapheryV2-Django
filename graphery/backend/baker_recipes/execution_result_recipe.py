from __future__ import annotations

from model_bakery.recipe import Recipe, foreign_key

from . import graph_anchor_recipe, code_recipe
from ..models import ExecutionResult

__all__ = ["execution_result_recipe"]


execution_result_recipe = Recipe(
    ExecutionResult,
    code=foreign_key(code_recipe),
    graph_anchor=foreign_key(graph_anchor_recipe),
)
