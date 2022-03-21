from strawberry.arguments import UNSET
from strawberry_django.type import process_type

from ..models import MixinBase

__all__ = ["graphql_type"]


# noinspection PyShadowingBuiltins
def graphql_type(model, *, filters=UNSET, **kwargs):
    if "fields" in kwargs or "types" in kwargs:
        from strawberry_django.legacy.type import type as type_legacy

        return type_legacy(model, **kwargs)

    def wrapper(cls):
        for c in reversed(model.__mro__[1:]):
            if issubclass(c, MixinBase) and c is not MixinBase:
                c.inject_graphql_types(cls)

        return process_type(cls, model, filters=filters, **kwargs)

    return wrapper


def graphql_input(model, *, partial=False, **kwargs):
    return graphql_type(model, partial=partial, is_input=True, **kwargs)


def graphql_mutation(model, **kwargs):
    return graphql_type(model, **kwargs)
