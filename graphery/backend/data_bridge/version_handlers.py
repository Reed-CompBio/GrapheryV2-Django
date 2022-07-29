from __future__ import annotations

from typing import TypeVar, Optional, Final

from django.utils import timezone
from django.http import HttpRequest

from ..models import Status, User, VersionMixin

_MODEL_INSTANCE = TypeVar("_MODEL_INSTANCE", bound=VersionMixin)
_MODEL_INFO = TypeVar("_MODEL_INFO")

__all__ = ["should_create_new_version", "IMPOSSIBLE"]


class _Impossible:
    pass


IMPOSSIBLE = _Impossible()
del _Impossible


class TimeDependent:
    """
    To indicate if a status condition is time dependent
    """

    def __init__(self, seconds: int, before: Optional[Status], after: Optional[Status]):
        self.seconds = seconds
        self.before = before
        self.after = after

    def get_status(self, time_diff: int):
        """
        if the time difference is less than the stored seconds,
        return the before status, otherwise return the after status
        """
        if time_diff < self.seconds:
            return self.before
        return self.after


AUTO_SAVE_MERGE_TIME: Final[int] = 600  # 600 seconds = 10 minutes


same_author_stored_requested_mapping = {
    Status.DRAFT: {
        Status.DRAFT: Status.DRAFT,
        Status.PUBLISHED: None,
        Status.REVIEWING: None,
        Status.PRIVATE: None,
        Status.TRASH: IMPOSSIBLE,
        Status.AUTOSAVE: Status.AUTOSAVE,
        Status.CLOSED: IMPOSSIBLE,
    },
    Status.PUBLISHED: {
        Status.DRAFT: Status.DRAFT,
        Status.PUBLISHED: None,
        Status.REVIEWING: Status.REVIEWING,
        Status.PRIVATE: None,
        Status.TRASH: IMPOSSIBLE,
        Status.AUTOSAVE: Status.AUTOSAVE,
        Status.CLOSED: None,
    },
    Status.REVIEWING: {
        Status.DRAFT: IMPOSSIBLE,
        Status.PUBLISHED: None,
        Status.REVIEWING: None,
        Status.PRIVATE: None,
        Status.TRASH: IMPOSSIBLE,
        Status.AUTOSAVE: IMPOSSIBLE,
        Status.CLOSED: IMPOSSIBLE,
    },
    Status.PRIVATE: {
        Status.DRAFT: Status.DRAFT,
        Status.PUBLISHED: None,
        Status.REVIEWING: None,
        Status.PRIVATE: None,
        Status.TRASH: IMPOSSIBLE,
        Status.AUTOSAVE: Status.AUTOSAVE,
        Status.CLOSED: None,
    },
    Status.TRASH: {
        Status.DRAFT: IMPOSSIBLE,
        Status.PUBLISHED: IMPOSSIBLE,
        Status.REVIEWING: IMPOSSIBLE,
        Status.PRIVATE: IMPOSSIBLE,
        Status.TRASH: IMPOSSIBLE,
        Status.AUTOSAVE: IMPOSSIBLE,
        Status.CLOSED: IMPOSSIBLE,
    },
    Status.AUTOSAVE: {
        Status.DRAFT: None,
        Status.PUBLISHED: None,
        Status.REVIEWING: None,
        Status.PRIVATE: None,
        Status.TRASH: IMPOSSIBLE,
        Status.AUTOSAVE: TimeDependent(AUTO_SAVE_MERGE_TIME, None, Status.AUTOSAVE),
        Status.CLOSED: IMPOSSIBLE,
    },
    Status.CLOSED: {
        Status.DRAFT: IMPOSSIBLE,
        Status.PUBLISHED: None,
        Status.REVIEWING: None,
        Status.PRIVATE: IMPOSSIBLE,
        Status.TRASH: IMPOSSIBLE,
        Status.AUTOSAVE: IMPOSSIBLE,
        Status.CLOSED: None,
    },
}


different_author_stored_requested_mapping = {
    Status.DRAFT: {
        Status.DRAFT: Status.DRAFT,
        Status.PUBLISHED: None,
        Status.REVIEWING: None,
        Status.PRIVATE: None,
        Status.TRASH: IMPOSSIBLE,
        Status.AUTOSAVE: Status.AUTOSAVE,
        Status.CLOSED: IMPOSSIBLE,
    },
    Status.PUBLISHED: {
        Status.DRAFT: Status.DRAFT,
        Status.PUBLISHED: None,
        Status.REVIEWING: Status.REVIEWING,
        Status.PRIVATE: None,
        Status.TRASH: IMPOSSIBLE,
        Status.AUTOSAVE: Status.AUTOSAVE,
        Status.CLOSED: None,
    },
    Status.REVIEWING: {
        Status.DRAFT: IMPOSSIBLE,
        Status.PUBLISHED: None,
        Status.REVIEWING: None,
        Status.PRIVATE: None,
        Status.TRASH: IMPOSSIBLE,
        Status.AUTOSAVE: IMPOSSIBLE,
        Status.CLOSED: IMPOSSIBLE,
    },
    Status.PRIVATE: {
        Status.DRAFT: Status.DRAFT,
        Status.PUBLISHED: None,
        Status.REVIEWING: None,
        Status.PRIVATE: None,
        Status.TRASH: IMPOSSIBLE,
        Status.AUTOSAVE: Status.AUTOSAVE,
        Status.CLOSED: None,
    },
    Status.TRASH: {
        Status.DRAFT: IMPOSSIBLE,
        Status.PUBLISHED: IMPOSSIBLE,
        Status.REVIEWING: IMPOSSIBLE,
        Status.PRIVATE: IMPOSSIBLE,
        Status.TRASH: IMPOSSIBLE,
        Status.AUTOSAVE: IMPOSSIBLE,
        Status.CLOSED: IMPOSSIBLE,
    },
    Status.AUTOSAVE: {
        Status.DRAFT: Status.DRAFT,
        Status.PUBLISHED: None,
        Status.REVIEWING: None,
        Status.PRIVATE: None,
        Status.TRASH: IMPOSSIBLE,
        Status.AUTOSAVE: Status.AUTOSAVE,
        Status.CLOSED: IMPOSSIBLE,
    },
    Status.CLOSED: {
        Status.DRAFT: IMPOSSIBLE,
        Status.PUBLISHED: None,
        Status.REVIEWING: None,
        Status.PRIVATE: IMPOSSIBLE,
        Status.TRASH: IMPOSSIBLE,
        Status.AUTOSAVE: IMPOSSIBLE,
        Status.CLOSED: None,
    },
}


def should_create_new_version(
    head_object: _MODEL_INSTANCE,
    request: Optional[HttpRequest],
    model_info: _MODEL_INFO,
    requested_time: int = None,
) -> Optional[Status | IMPOSSIBLE]:
    """
    Returns if a new version should be created for the given request.
    When None is returned, no new version should be created.
    When IMPOSSIBLE is returned, Exception should be raised
    When a Status is returned, a new version should be created.

    :param head_object: The head object of the current version
    :param request:
    :param model_info: The model info of requested change
    :param requested_time: The time when the request was made
    """
    if request is None:
        return IMPOSSIBLE

    requested_by: User = request.user

    if requested_by != head_object.edited_by:
        result = different_author_stored_requested_mapping[head_object.item_status][
            model_info.item_status
        ]
    else:
        result = same_author_stored_requested_mapping[head_object.item_status][
            model_info.item_status
        ]

    if isinstance(result, TimeDependent):
        requested_time = requested_time or timezone.now()
        return result.get_status((requested_time - head_object.modified_time).seconds)

    return result
