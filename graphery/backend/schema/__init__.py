from types import NoneType

from typing import List, Optional

import strawberry
from strawberry.django import auth

from .permissions import AdminPermission
from .resolvers import (
    resolve_tag_anchors,
    resolve_current_user,
    resolve_tutorial_anchors,
    resolve_graph_anchors,
)
from ..types import UserType, TagAnchorType

__all__ = ["schema"]


@strawberry.type
class Query:
    me: Optional[UserType] = strawberry.field(resolver=resolve_current_user)
    tag_anchors: List[Optional[TagAnchorType]] = strawberry.field(
        resolver=resolve_tag_anchors,
    )
    tutorial_anchors: List[Optional[TagAnchorType]] = strawberry.field(
        resolver=resolve_tutorial_anchors,
    )
    graph_anchors: List[Optional[TagAnchorType]] = strawberry.field(
        resolver=resolve_graph_anchors,
    )


@strawberry.type
class Mutation:
    login: Optional[UserType] = auth.login()
    logout: NoneType = auth.logout()


schema = strawberry.Schema(query=Query, mutation=Mutation)
