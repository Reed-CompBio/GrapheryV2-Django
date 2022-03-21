from __future__ import annotations

from typing import Optional, List

from strawberry.django import auto
from ..models import TagAnchor, Tag
from .utils import graphql_type

__all__ = ["TagAnchorType", "TagType"]


@graphql_type(Tag)
class TagType:
    name: str
    tag_anchor: TagAnchorType
    description: str


@graphql_type(TagAnchor)
class TagAnchorType:
    anchor_name: str
    tags: List[Optional[TagType]]
