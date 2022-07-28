from __future__ import annotations

import datetime

import requests
from django.conf import settings
from typing import TypedDict, Literal, Final, Dict, Optional, List

__all__ = [
    "site_verify_recaptcha",
    "VerifyRequest",
    "VerifyResponse",
    "RecaptchaErrorCodesMsg",
    "RECAPTCHA_ON",
]


if settings.G_RECAPTCHA_ON or settings.G_RECAPTCHA_SECRET:
    if not settings.G_RECAPTCHA_ON or not settings.G_RECAPTCHA_SECRET:
        raise ValueError("ReCaptcha is not set properly")
    RECAPTCHA_ON = True
else:
    RECAPTCHA_ON = False


RECAPTCHA_URL = "https://www.google.com/recaptcha/api/siteverify"

RecaptchaErrorCodesMsg: Final[Dict[str, str]] = {
    "missing-input-secret": "The secret parameter is missing.",
    "invalid-input-secret": "The secret parameter is invalid or malformed.",
    "missing-input-response": "The response parameter is missing.",
    "invalid-input-response": "The response parameter is invalid or malformed.",
    "bad-request": "The request is invalid or malformed.",
    "timeout-or-duplicate": "The response is no longer valid: either is too old or has been used previously.",
}

ReCaptchaErrorCodesType = Literal[
    "missing-input-secret",
    "invalid-input-secret",
    "missing-input-response",
    "invalid-input-response",
    "bad-request",
    "timeout-or-duplicate",
]


class VerifyRequest(TypedDict):
    secret: str
    response: str  # the response token from client html. terrible naming lol
    # noinspection SpellCheckingInspection
    remoteip: Optional[str]


class VerifyResponse(TypedDict, total=False):
    success: bool
    score: float
    action: str
    challenge_ts: str | datetime.datetime
    hostname: str
    error_codes: Optional[List[ReCaptchaErrorCodesType]]


def site_verify_recaptcha(token: str, remote_ip: str | None = None) -> VerifyResponse:
    if not RECAPTCHA_ON:
        return VerifyResponse(success=True, score=1.0)

    request = VerifyRequest(
        secret=settings.G_RECAPTCHA_SECRET, response=token, remoteip=remote_ip
    )
    return requests.post(RECAPTCHA_URL, json=request).json()
