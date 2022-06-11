from __future__ import annotations

import strawberry_django
from strawberry import auto

from .utils import mixin_filter
from ..models import Tutorial, User, TutorialAnchor, GraphAnchor, TagAnchor, Tag, Graph

__all__ = [
    "TagAnchorFilter",
    "TagFilter",
    "UserFilter",
    "TutorialAnchorFilter",
    "TutorialFilter",
    "GraphAnchorFilter",
    "GraphFilter",
]


@mixin_filter(TagAnchor, lookups=True)
class TagAnchorFilter:
    anchor_name: auto
    tags: auto


@mixin_filter(Tag, lookups=True)
class TagFilter:
    tag_anchor: TagAnchorFilter


@strawberry_django.filters.filter(User, lookups=True)
class UserFilter:
    displayed_name: auto


@mixin_filter(TutorialAnchor, lookups=True)
class TutorialAnchorFilter:
    url: auto
    anchor_name: auto
    tutorials: TutorialFilter


@mixin_filter(Tutorial, lookups=True)
class TutorialFilter:
    tutorial_anchor: TutorialAnchorFilter
    title: auto
    abstract: auto
    content_markdown: auto
    authors: UserFilter


@mixin_filter(GraphAnchor, lookups=True)
class GraphAnchorFilter:
    url: auto
    anchor_name: auto


@mixin_filter(Graph, lookups=True)
class GraphFilter:
    graph_anchor: GraphAnchorFilter
    makers: UserFilter
