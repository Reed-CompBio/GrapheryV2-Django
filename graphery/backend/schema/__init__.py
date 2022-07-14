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
from .resolvers.queries import (
    resolve_tutorial_anchors,
    resolve_graph_anchors,
    get_tutorial_content,
    get_graph,
    get_graph_content,
    get_code,
)
from ..executor_runner.executor_connect import handle_request
from ..executor_runner.types import ResponseType
from ..models import Code
from ..types import (
    UserType,
    TagAnchorType,
    TutorialType,
    TutorialAnchorType,
    GraphAnchorType,
    GraphType,
    GraphDescriptionType,
)

from ..types.filters import (
    TagAnchorFilter,
)

__all__ = ["schema"]


@strawberry.type
class Query:
    me: Optional[UserType] = strawberry.field(resolver=resolve_current_user)
    tag_anchors: List[TagAnchorType] = strawberry_django.field(filters=TagAnchorFilter)
    tutorial_anchors: List[TutorialAnchorType] = strawberry_django.field(
        resolve_tutorial_anchors
    )
    graph_anchors: List[GraphAnchorType] = strawberry_django.field(
        resolve_graph_anchors
    )
    tutorial_content: Optional[TutorialType] = strawberry_django.field(
        get_tutorial_content
    )
    graph_content: Optional[GraphDescriptionType] = strawberry_django.field(
        get_graph_content
    )
    graph: Optional[GraphType] = strawberry_django.field(get_graph)
    code: Optional[Code] = strawberry_django.field(get_code)


@strawberry.type
class Mutation:
    login: Optional[UserType] = auth.login()
    register: Optional[UserType] = strawberry.mutation(
        resolver=resolve_user_register_mutation
    )
    logout: NoneType = auth.logout()
    execution_request: ResponseType = strawberry.mutation(handle_request)


schema = strawberry.Schema(query=Query, mutation=Mutation)
