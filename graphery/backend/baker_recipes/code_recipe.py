from __future__ import annotations

from model_bakery.recipe import Recipe, foreign_key

from . import tutorial_anchor_recipe
from ..data_bridge import black_format_str
from ..models import Code

__all__ = ["code_recipe"]


ORIGINAL_CODE = """\
def test_code(ele):
    print(ele)
"""

BLACKED_CODE = black_format_str(ORIGINAL_CODE)

code_recipe = Recipe(
    Code,
    tutorial_anchor=foreign_key(tutorial_anchor_recipe, one_to_one=True),
    code=BLACKED_CODE,
)
