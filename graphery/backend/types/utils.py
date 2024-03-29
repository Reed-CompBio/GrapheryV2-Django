from typing import Sequence

import strawberry_django.filters
from strawberry import UNSET
from strawberry_django.type import process_type

from ..models import MixinBase

__all__ = ["graphql_type", "graphql_input", "graphql_mutation", "mixin_filter"]


def graphql_type(
    model,
    *,
    filters=UNSET,
    inject_mixin_fields: bool | Sequence[MixinBase] = True,
    **kwargs,
):
    def wrapper(cls):
        if inject_mixin_fields:
            if isinstance(inject_mixin_fields, Sequence):
                for c in reversed(model.__mro__[1:]):
                    if c in inject_mixin_fields:
                        c.inject_graphql_types(cls)
            else:
                for c in reversed(model.__mro__[1:]):
                    if issubclass(c, MixinBase) and c is not MixinBase:
                        c.inject_graphql_types(cls)

        return process_type(cls, model, filters=filters, **kwargs)

    return wrapper


def graphql_input(model, *, partial=False, **kwargs):
    return graphql_type(model, partial=partial, is_input=True, **kwargs)


def graphql_mutation(model, **kwargs):
    return graphql_type(model, **kwargs)


def mixin_filter(model, *, inject_mixin_fields=True, name=None, lookups=False):
    def wrapper(cls):
        if inject_mixin_fields:
            if isinstance(inject_mixin_fields, Sequence):
                for c in reversed(model.__mro__[1:]):
                    if c in inject_mixin_fields:
                        c.inject_graphql_types(cls)
            else:
                for c in reversed(model.__mro__[1:]):
                    if issubclass(c, MixinBase) and c is not MixinBase:
                        c.inject_graphql_types(cls)

        return strawberry_django.filters.filter(model, name=name, lookups=lookups)(cls)

    return wrapper
