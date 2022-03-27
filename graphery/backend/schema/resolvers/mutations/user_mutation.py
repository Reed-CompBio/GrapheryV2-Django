from __future__ import annotations

from typing import Optional

from strawberry.types import Info

from ....types import (
    UserType,
    UserMutationType,
)

__all__ = ["resolve_user_register_mutation"]


def resolve_user_register_mutation(
    info: Info, user: UserMutationType
) -> Optional[UserType]:
    pass
