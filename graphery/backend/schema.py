from typing import List

import strawberry
from strawberry.django import auth
from strawberry.types import Info

from .models import TagAnchor
from .types import UserType, TagAnchorType


@strawberry.type
class Query:
    me: UserType = auth.current_user()

    @strawberry.field
    def tag_anchors(self, info: Info) -> List[TagAnchorType]:
        return TagAnchor.objects.all()


@strawberry.type
class Mutation:
    login: UserType = auth.login()
    logout = auth.logout()


schema = strawberry.Schema(query=Query, mutation=Mutation)
