import strawberry
from strawberry.django import auth
from .types import User


@strawberry.type
class Query:
    me: User = auth.current_user()


@strawberry.type
class Mutation:
    login: User = auth.login()
    logout = auth.logout()


schema = strawberry.Schema(query=Query, mutation=Mutation)
