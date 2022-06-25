from types import NoneType

from typing import List, Optional

import strawberry
import strawberry_django
from strawberry.django import auth

from .permissions import AdminPermission
from .resolvers import (
    resolve_current_user,
    resolve_user_register_mutation,
)
from .resolvers.mutations.user_mutation import resolve_tag_mutation
from .resolvers.queries import (
    resolve_tutorial_anchors,
    resolve_graph_anchors,
    get_tutorial_content,
    get_graph_content,
    get_graph_anchor,
)
from ..types import (
    UserType,
    TagAnchorType,
    TutorialType,
    TutorialAnchorType,
    GraphAnchorType,
    GraphDescriptionType,
    GraphType,
)

from ..types.filters import (
    TagAnchorFilter,
)

__all__ = ["schema"]


@strawberry.type
class Query:
    me: Optional[UserType] = strawberry.field(resolver=resolve_current_user)
    tag_anchors: List[Optional[TagAnchorType]] = strawberry_django.field(
        filters=TagAnchorFilter
    )
    tutorial_anchors: List[Optional[TutorialAnchorType]] = strawberry_django.field(
        resolve_tutorial_anchors
    )
    graph_anchors: List[Optional[GraphAnchorType]] = strawberry_django.field(
        resolve_graph_anchors,
    )
    tutorial_content: Optional[TutorialType] = strawberry_django.field(
        get_tutorial_content,
    )
    graph_content: List[Optional[GraphDescriptionType]] = strawberry_django.field(
        get_graph_content,
    )
    graph: Optional[GraphType] = strawberry_django.field(get_graph_anchor)


@strawberry.type
class Mutation:
    login: Optional[UserType] = auth.login()
    logout: NoneType = auth.logout()


schema = strawberry.Schema(query=Query, mutation=Mutation)
