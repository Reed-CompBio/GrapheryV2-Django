from __future__ import annotations

from model_bakery import seq
from model_bakery.recipe import Recipe, foreign_key, related

from . import tag_anchor_recipe, user_recipe
from ..models import TutorialAnchor, Tutorial


TUTORIAL_ANCHOR_NAME = "tutorial anchor"

__all__ = ["TUTORIAL_ANCHOR_NAME", "tutorial_anchor_recipe", "tutorial_recipe"]


tutorial_anchor_recipe = Recipe(
    TutorialAnchor,
    anchor_name=seq(TUTORIAL_ANCHOR_NAME),
    tag_anchors=related(tag_anchor_recipe),
)

tutorial_recipe = Recipe(
    Tutorial,
    tutorial_anchor=foreign_key(tutorial_anchor_recipe),
    authors=related(user_recipe),
)
