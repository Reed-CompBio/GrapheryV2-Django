from __future__ import annotations

from model_bakery.recipe import Recipe, related

from . import tutorial_anchor_recipe, graph_anchor_recipe
from ..models import Uploads

__all__ = ["uploads_recipe"]


uploads_recipe = Recipe(
    Uploads,
    tutorial_anchors=related(tutorial_anchor_recipe),
    graph_anchors=related(graph_anchor_recipe),
    _create_files=False,
)
