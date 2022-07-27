from __future__ import annotations

import json

import pytest
from asgiref.sync import sync_to_async
from django.contrib.sessions.middleware import SessionMiddleware
from typing import Optional, Type, Sequence, TypeVar, Generic, Dict, List

from django.db.models import Model, ManyToManyRel
from django.db.models.fields.related import ManyToManyField
from django.http import HttpResponse, HttpRequest
from strawberry import UNSET
from strawberry.django.context import StrawberryDjangoContext

from ..data_bridge import DataBridgeBase, ValidationError, black_format_str
from ..models import UserRoles, User


def make_django_context(
    request: HttpRequest, response: Optional[HttpResponse] = None
) -> StrawberryDjangoContext:
    return StrawberryDjangoContext(request, response or HttpResponse())


async_make_django_context = sync_to_async(make_django_context)


def save_session_in_request(
    request: HttpRequest, session_mw: SessionMiddleware
) -> HttpRequest:
    session_mw.process_request(request)
    request.session.save()

    return request


async_save_session_in_request = sync_to_async(save_session_in_request)


def make_request_with_user(rf: "RequestFactory", user: User) -> HttpRequest:
    request = rf.post("/graphql/sync", data=None, content_type="application/json")
    request.user = user
    return request


USER_LIST = ["admin_user", "editor_user", "author_user", "visitor_user", "reader_user"]


_T = TypeVar("_T", bound=Model)
_S = TypeVar("_S")


_EXPECTED_VALUE = TypeVar("_EXPECTED_VALUE")
_ACTUAL_VALUE = TypeVar("_ACTUAL_VALUE")


class FieldChecker(Generic[_EXPECTED_VALUE, _ACTUAL_VALUE]):
    def __init__(self, *, field_name: str = UNSET) -> None:
        self._field_name = field_name
        self._expected_value = UNSET
        self._actual_value = UNSET

    @property
    def field_name(self) -> str:
        return "UNSET" if self._field_name is UNSET else self._field_name

    def set_expected_value(self, expected_value: _EXPECTED_VALUE) -> FieldChecker:
        if isinstance(self._actual_value, Model):
            assert hasattr(expected_value, "id")
            self._expected_value = self._actual_value.__class__.objects.get(
                id=expected_value.id
            )
        elif isinstance(self._actual_value, set):
            self._expected_value = {
                expected_item
                if isinstance(expected_item, Model)
                else expected_item._django_type.model.objects.get(id=expected_item.id)
                for expected_item in expected_value
            }
        else:
            self._expected_value = expected_value

        assert (
            self._expected_value is not UNSET
        ), f"expected {self._field_name} is not set, the input is {expected_value}"

        return self

    def get_actual_value(
        self, model_instance: Model, field_name: str = UNSET
    ) -> FieldChecker:
        self._field_name = field_name or self._field_name

        if self._field_name is UNSET:
            raise ValueError(
                f"When setting actual value for {model_instance}, the field name is None"
            )

        self._actual_value = getattr(model_instance, self._field_name)

        if isinstance(
            model_instance._meta.get_field(self._field_name),
            (ManyToManyField, ManyToManyRel),
        ):
            self._actual_value = set(self._actual_value.all())

        assert (
            self._actual_value is not UNSET
        ), f"actual {self._field_name} is not set, the input is {model_instance}"

        return self

    def _check(self) -> None:
        assert (
            self._actual_value == self._expected_value
        ), f"Expected {self._expected_value} for field '{self._field_name}' but got {self._actual_value}"

    def check(self) -> None:
        if self._expected_value is UNSET or self._actual_value is UNSET:
            raise ValueError("The expected value or actual value is not set")

        self._check()

    def __str__(self):
        return f'FieldChecker("{self.field_name}")'

    def __repr__(self):
        return f"FieldChecker for '{self.field_name}'"


_DEFAULT_FIELD_CHECKER = FieldChecker()


class JSONChecker(FieldChecker):
    def set_expected_value(
        self, expected_value: str | Dict | List | int | float
    ) -> FieldChecker:
        if isinstance(expected_value, str):
            self._expected_value = json.loads(expected_value)
        else:
            self._expected_value = expected_value

        return self


def instance_to_model_info(
    model_instance: _T, data_cls: Type[_S], ignore_value: Sequence[str] | str = ()
) -> _S:
    """
    convert a model instance to a model info
    all the fields in the data_cls will be collected except those in ignore_value
    :param model_instance: the model instance to be converted
    :param data_cls: the data class type
    :param ignore_value: field names to be ignored
    :return:
    """
    instance = data_cls()

    if isinstance(ignore_value, str):
        ignore_value = (ignore_value,)

    for field_name in instance.__dict__.keys():
        if field_name in ignore_value:
            continue

        val = getattr(model_instance, field_name, UNSET)
        if isinstance(
            model_instance._meta.get_field(field_name), (ManyToManyField, ManyToManyRel)
        ):
            val = val.all()

        setattr(instance, field_name, val)

    return instance


def match_model_info_and_model_instance(
    model_instance, model_info, custom_checkers: Sequence[FieldChecker] = ()
):
    """
    test if model_info and model_instance are equal
    if some field in the model info is empty, it will be ignored
    if some field is specified in custom_checker, it will be checked with that checker
    otherwise it will be checked with the default ==

    :param model_instance:
    :param model_info:
    :param custom_checkers:
    :return:
    """
    custom_checkers: Dict[str, FieldChecker] = {
        custom_checker.field_name: custom_checker
        for custom_checker in custom_checkers
        if isinstance(custom_checker, FieldChecker)
    }

    for field_name, target_value in model_info.__dict__.items():

        if target_value is UNSET:
            continue

        custom_checkers.get(field_name, _DEFAULT_FIELD_CHECKER).get_actual_value(
            model_instance, field_name
        ).set_expected_value(target_value).check()


def bridge_test_helper(
    bridge_cls: Type[DataBridgeBase],
    new_model_info,
    old_model_info=None,
    request: HttpRequest = None,
    min_edit_user_role: int | UserRoles = -1,
    min_delete_user_role: int | UserRoles = -1,
    is_deleting: bool = False,
    delete_fail: bool = False,
    custom_checker: Sequence[FieldChecker] = (),
) -> None:
    """
    Helper function for testing bridges.
    :param bridge_cls: the bridge class to test, should be a subclass of DataBridgeBase
    :param new_model_info: the model info to be applied
    :param old_model_info: the old model info
    :param request: the request object (HTTPRequest) to use for the test
    :param min_edit_user_role: the minimum user role required by the bridge
    :param min_delete_user_role: the minimum user role required by the bridge to delete
    :param is_deleting: whether the bridge is deleting
    :param delete_fail: whether the bridge should fail to delete
    :param custom_checker: a list of custom checkers
    :return:
    """

    user: User = request and request.user
    bridged_model: Type[Model] | None = bridge_cls.bridged_model_cls
    assert bridged_model is not None

    if is_deleting:
        if min_delete_user_role >= 0:
            assert bridge_cls.minimal_delete_user_role == min_delete_user_role

        if delete_fail or user.role < min_delete_user_role:
            with pytest.raises(ValidationError):
                bridge_cls(new_model_info.id).get_instance().delete_model_instance(
                    request=request
                )
        else:
            bridge_cls(new_model_info.id).get_instance().delete_model_instance(
                request=request
            )
    else:
        assert bridge_cls.minimal_edit_user_role == min_edit_user_role

        if min_edit_user_role >= 0 and user.role < min_edit_user_role:
            with pytest.raises(ValidationError):
                bridge_cls.bridges_from_model_info(old_model_info, request=request)
            instance = bridged_model.objects.get(id=new_model_info.id)
            assert old_model_info is not None
            match_model_info_and_model_instance(
                instance, old_model_info, custom_checker
            )
        else:
            bridge_cls.bridges_from_model_info(new_model_info, request=request)
            try:
                instance = bridged_model.objects.get(id=old_model_info.id)
            except bridged_model.DoesNotExist:
                assert (
                    bridge_cls.attaching_to is not None
                ), "Model instance not found when attaching_to is empty"

                assert any(
                    getattr(new_model_info, attaching_to_field) is UNSET
                    for attaching_to_field in bridge_cls.attaching_to
                ), f"None of the attaching_to fields {bridge_cls.attaching_to} is empty, but {bridged_model} does not exist"
            else:
                assert bridge_cls.attaching_to is None or all(
                    getattr(new_model_info, attaching_to_field) is not UNSET
                    for attaching_to_field in bridge_cls.attaching_to
                ), f"Some of the attaching_to fields {bridge_cls.attaching_to} is empty, but {bridged_model} still exists"

                match_model_info_and_model_instance(
                    instance, new_model_info, custom_checker
                )


ORIGINAL_TEST_CODE = """\
def test_code(self, ele, *args, kw_ele, **kwargs,):
    e1,e2=args
    new_ele = e1*ele*e2^kw_ele
    print(new_ele, kwargs)
"""


BLACKED_TEST_CODE = black_format_str(ORIGINAL_TEST_CODE)

EXAMPLE_CODE = """\
def test_code(
    self,
    ele,
    *args,
    kw_ele,
    **kwargs,
):
    e1, e2 = args
    new_ele = e1 * ele * e2 ^ kw_ele
    print(new_ele, kwargs)
"""


def test_black_code():
    assert BLACKED_TEST_CODE == EXAMPLE_CODE
