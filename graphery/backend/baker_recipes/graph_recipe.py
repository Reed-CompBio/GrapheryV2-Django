from __future__ import annotations

from model_bakery import seq
from model_bakery.recipe import Recipe, related, foreign_key

from . import tag_anchor_recipe, user_recipe
from ..models import GraphAnchor, OrderedGraphAnchor, Graph, GraphDescription


GRAPH_ANCHOR_NAME = "graph anchor"
GRAPH_DESCRIPTION_TITLE = "Graph Description Title"

__all__ = [
    "GRAPH_ANCHOR_NAME",
    "GRAPH_DESCRIPTION_TITLE",
    "graph_anchor_recipe",
    "ordered_graph_anchor_recipe",
    "graph_recipe",
    "graph_description_recipe",
]


graph_anchor_recipe = Recipe(
    GraphAnchor,
    anchor_name=seq(GRAPH_ANCHOR_NAME),
    tag_anchors=related(tag_anchor_recipe),
)

ordered_graph_anchor_recipe = Recipe(
    OrderedGraphAnchor,
    graph_anchor=related(graph_anchor_recipe),
    tutorial_anchor=related(tag_anchor_recipe),
)

graph_recipe = Recipe(
    Graph,
    graph_anchor=foreign_key(graph_anchor_recipe, one_to_one=True),
    makers=related(user_recipe),
)

graph_description_recipe = Recipe(
    GraphDescription,
    graph_anchor=foreign_key(graph_anchor_recipe),
    authors=related(user_recipe),
    title=seq(GRAPH_DESCRIPTION_TITLE),
)
