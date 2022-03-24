from __future__ import annotations

from typing import Optional

from strawberry.types import Info

from ..models import User


def get_user_from_info(info: Info) -> Optional[User]:
    if hasattr(info.context, "request"):
        request = info.context.request
        if request.user.is_authenticated:
            return request.user
    return None
