from __future__ import annotations

import time

import requests
from django.http import HttpRequest
from strawberry.types import Info
from django.conf import settings
import dataclasses

from .types import RequestType, ResponseType, RequestTypeJSON, ErrorType, InfoType
from ..models import User, UserRoles

GRAPHERY_EXECUTOR_ACCESS_TIME_SESSION_NAME = "graphery_executor_access_time"

__all__ = ["handle_executor_request"]


def request_type_to_json(request_type: RequestType) -> RequestTypeJSON:
    request_type: dataclasses.dataclass
    return dataclasses.asdict(request_type)


def make_request(request_obj: RequestType) -> ResponseType:
    request_json = request_type_to_json(request_obj)
    result_json = requests.post(
        settings.GRAPHERY_EXECUTOR_URL, json=request_json
    ).json()

    errors = result_json["errors"]
    info = result_json["info"]

    return ResponseType(
        errors=[
            ErrorType(message=error["message"], traceback=error["traceback"])
            for error in result_json["errors"]
        ]
        if errors
        else None,
        info=InfoType(result=info["result"]) if info else None,
    )


def check_session_access_time(request: HttpRequest) -> None:
    user: User = request.user
    if user.is_authenticated and user.role > UserRoles.READER:
        # if the user is authenticated and has a role greater than reader,
        # then the request should be passed
        return

    # if the user is not authenticated or has a role less than reader,
    last_time = request.session.get(GRAPHERY_EXECUTOR_ACCESS_TIME_SESSION_NAME, None)

    # we check the if it had bad any request
    # if not, record the time and let it pass
    # otherwise, we check if the request is too frequent
    if last_time is not None:
        if (
            time.time() - last_time
        ) < settings.GRAPHERY_EXECUTOR_ACCESS_INTERVAL_SECONDS:
            raise Exception("Too many requests")


def set_session_access_time(request: HttpRequest) -> None:
    request.session[GRAPHERY_EXECUTOR_ACCESS_TIME_SESSION_NAME] = time.time()
    request.session.modified = True


def handle_executor_request(info: Info, request: RequestType) -> ResponseType:
    http_request: HttpRequest = info.context.request
    check_session_access_time(http_request)
    result = make_request(request)
    set_session_access_time(http_request)

    return result
