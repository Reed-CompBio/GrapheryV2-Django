from asgiref.sync import sync_to_async
from django.contrib.sessions.middleware import SessionMiddleware
from typing import Optional

from django.http import HttpResponse, HttpRequest
from strawberry.django.context import StrawberryDjangoContext


def make_django_context(
    request: HttpRequest, response: Optional[HttpResponse] = None
) -> StrawberryDjangoContext:
    return StrawberryDjangoContext(request, response or HttpResponse())


async_make_django_context = sync_to_async(make_django_context)


def save_session_in_request(
    request: HttpRequest, session_mw: SessionMiddleware
) -> None:
    session_mw.process_request(request)
    request.session.save()


async_save_session_in_request = sync_to_async(save_session_in_request)
