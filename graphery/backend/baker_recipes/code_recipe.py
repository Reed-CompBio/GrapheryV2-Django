from __future__ import annotations

from model_bakery.recipe import Recipe, foreign_key

from . import tutorial_anchor_recipe
from ..models import Code

__all__ = ["code_recipe"]


code_recipe = Recipe(
    Code,
    tutorial_anchor=foreign_key(tutorial_anchor_recipe, one_to_one=True),
)
