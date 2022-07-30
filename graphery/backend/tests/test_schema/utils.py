from __future__ import annotations

from typing import (
    Dict,
    Type,
    Any,
    TypeVar,
    Generic,
    Iterable,
    Callable,
    TypedDict,
    Optional,
    List,
)

from django.contrib.sessions.middleware import SessionMiddleware
from django.db import models
from strawberry import UNSET

from ..utils import make_request_with_user, save_session_in_request, make_django_context
from ...models import User
from ...schema import schema


_T = TypeVar("_T", bound=models.Model)


class ModelMutationVariable(TypedDict):
    op: str
    data: Dict[str, Any]


class ExecutorMutationOptionVariable(TypedDict, total=False):
    randSeed: Optional[int]
    floatPrecision: Optional[int]
    inputList: Optional[List[str]]


class ExecutorMutationVariable(TypedDict):
    code: str
    graph: str
    version: str
    options: Optional[ExecutorMutationOptionVariable]


class MutationChecker(Generic[_T]):
    """
    make a mutation and performs checks on the result
    """

    def __init__(
        self,
        mutation: str,
        rf,
        variables: Optional[ModelMutationVariable | ExecutorMutationVariable] = None,
        user: User = None,
        session_middleware: SessionMiddleware = None,
        has_error: bool = False,
        count_change: int | None = None,
        model_cls: Type[_T] = None,
        equals: Dict[str, Any] = None,
        not_equals: Dict[str, Any] = None,
        diff: Iterable[str] = None,
        same: Iterable[str] = None,
        compare: Dict[str, Callable[[Any, Any], Any]] = None,
        old_instance: _T = None,
    ):
        self.request = make_request_with_user(rf, user)
        if session_middleware:
            save_session_in_request(self.request, session_middleware)
        self.context = make_django_context(self.request)

        self.variables = variables
        self.has_error = has_error
        self.count_change = count_change
        self.model_cls = model_cls

        if self.count_change is not None:
            self.old_count = self.model_cls.objects.all().count()
        else:
            self.old_count = None

        self.result = schema.execute_sync(
            mutation, variable_values=variables, context_value=self.context
        )

        self.checks = {
            "equals": equals,
            "not_equals": not_equals,
            "diff": diff,
            "same": same,
            "compare": compare,
        }

        self.new_instance: _T | None = None
        self.old_instance: _T | None = old_instance
        if self.old_instance:
            self.old_instance.pk = None

    @property
    def equals(self):
        return self.checks["equals"]

    @property
    def not_equals(self):
        return self.checks["not_equals"]

    @property
    def diff(self):
        return self.checks["diff"]

    @property
    def same(self):
        return self.checks["same"]

    @property
    def compare(self):
        return self.checks["compare"]

    def set_new_instance(self, instance: _T | UNSET = UNSET):
        if instance is UNSET:
            instance = self.model_cls.objects.get(id=self.variables["data"]["id"])

        self.new_instance = instance
        return self

    def set_old_instance(self, instance: _T):
        self.old_instance = instance
        self.old_instance.pk = None
        return self

    def check(self):
        if self.has_error:
            assert self.result.errors, "expected error but got none"
        else:
            assert (
                self.result.errors is None
            ), f"expected no error but got some, {self.result.errors}"

        if self.old_count is not None:
            assert (actual := self.model_cls.objects.all().count()) == (
                expected := self.old_count + self.count_change
            ), f"count change failed, actual: {actual}, expected: {expected}"

        for check_type, check_data in self.checks.items():
            getattr(self, f"check_{check_type}")()

        return self

    def check_equals(self):
        if self.equals is not None:
            for key, value in self.equals.items():
                assert hasattr(
                    self.new_instance, key
                ), f"{key} not found in {self.new_instance}"

                assert (
                    actual := getattr(self.new_instance, key, UNSET)
                ) == value, f"equal check failed for '{key}', actual: '{actual}', expected: '{value}'"

    def check_not_equals(self):
        if self.not_equals is not None:
            for key, value in self.not_equals.items():
                assert hasattr(
                    self.new_instance, key
                ), f"{key} not found in {self.new_instance}"

                assert (
                    actual := getattr(self.new_instance, key, UNSET)
                ) != value, f"not equal check failed for '{key}', actual: {actual}, expected: {value}"

    def check_diff(self):
        if self.diff is not None:
            for key in self.diff:
                assert (actual := getattr(self.new_instance, key, UNSET)) != (
                    expected := getattr(self.old_instance, key, UNSET)
                ), f"diff check failed for '{key}', actual: {actual}, expected: {expected}"

    def check_same(self):
        if self.same is not None:
            for key in self.same:
                assert (actual := getattr(self.new_instance, key, UNSET)) == (
                    expected := getattr(self.old_instance, key, UNSET)
                ), f"same check failed for '{key}', actual: {actual}, expected: {expected}"

    def check_compare(self):
        if self.compare is not None:
            for key, func in self.compare.items():
                assert func(
                    (new := getattr(self.new_instance, key, UNSET)),
                    (old := getattr(self.old_instance, key, UNSET)),
                ), f"compare check failed for '{key}', new: {new}, old: {old}"
