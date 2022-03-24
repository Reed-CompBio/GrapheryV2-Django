from __future__ import annotations

from strawberry.types import Info
from typing import Union, Awaitable, Any

from strawberry.permission import BasePermission

from .utils import get_user_from_info
from ..models import UserRoles


class AdminPermission(BasePermission):
    message = "You must be an admin to access this resource."

    def has_permission(
        self, source: Any, info: Info, **kwargs
    ) -> Union[bool, Awaitable[bool]]:
        user = get_user_from_info(info)
        if user is not None:
            # TODO fix this
            # user.has_perm("backend.can_view_tag_anchor")
            return True
        return False
