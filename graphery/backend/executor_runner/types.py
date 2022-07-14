from __future__ import annotations

from typing import Optional, List, TypedDict

import strawberry

from ..types.django_types import JSONType


@strawberry.input
class RequestOptionType:
    rand_seed: Optional[int]
    float_precision: Optional[int]
    input_list: Optional[List[str]]


@strawberry.input
class RequestType:
    code: str
    graph: str
    version: str
    options: Optional[RequestOptionType]


class RequestOptionTypeJSON(TypedDict):
    rand_seed: Optional[int]
    float_precision: Optional[int]
    input_list: Optional[List[str]]


class RequestTypeJSON(TypedDict):
    code: str
    graph: str
    version: str
    options: Optional[RequestOptionTypeJSON]


@strawberry.type
class ErrorType:
    message: str
    traceback: str


@strawberry.type
class InfoType:
    result: JSONType


@strawberry.type
class ResponseType:
    errors: Optional[List[ErrorType]]
    info: Optional[InfoType]
