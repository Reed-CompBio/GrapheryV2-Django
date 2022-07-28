from __future__ import annotations

from typing import Optional

from strawberry.types import Info

from ....data_bridge import UserBridge
from ....recaptcha import site_verify_recaptcha
from ....types import UserMutationType, UserType, OperationType

REGISTER_RECAPTCHA_MIN_SCORE = 0.7

__all__ = ["register_mutation"]


def register_mutation(
    info: Info, data: UserMutationType, recaptcha_token: Optional[str] = None
) -> Optional[UserType]:
    recaptcha_response = site_verify_recaptcha(token=recaptcha_token)
    if (
        recaptcha_response.get("success")
        and recaptcha_response.get("score") >= REGISTER_RECAPTCHA_MIN_SCORE
    ):
        return UserBridge.bridges_from_mutation(OperationType.CREATE, data, info=info)

    return None
