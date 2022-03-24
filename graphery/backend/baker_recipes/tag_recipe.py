from __future__ import annotations

from model_bakery import seq
from model_bakery.recipe import Recipe, foreign_key

from ..models import Tag, TagAnchor, LangCode

TAG_ANCHOR_NAME = "tag"

__all__ = [
    "TAG_ANCHOR_NAME",
    "tag_anchor_recipe",
    "tag_recipe",
    "lang_tag_recipe_maker",
]


tag_anchor_recipe = Recipe(
    TagAnchor,
    anchor_name=seq(TAG_ANCHOR_NAME),
)

tag_recipe = Recipe(
    Tag,
    tag_anchor=foreign_key(tag_anchor_recipe),
)


def lang_tag_recipe_maker(lang: str | LangCode) -> Recipe:
    return tag_recipe.extend(
        # TODO better naming
        name=seq(f"{TAG_ANCHOR_NAME}-{lang}"),
        lang_code=lang,
    )
