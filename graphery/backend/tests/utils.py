import pytest
from asgiref.sync import sync_to_async
from django.contrib.sessions.middleware import SessionMiddleware
from typing import Optional, Type, Sequence, Tuple

from django.db.models import Model
from django.db.models.fields.related import ManyToManyField
from django.http import HttpResponse, HttpRequest
from strawberry.arguments import UNSET
from strawberry.django.context import StrawberryDjangoContext

from ..data_bridge import DataBridgeBase, ValidationError
from ..models import UserRoles, User


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


USER_LIST = ["admin_user", "editor_user", "author_user", "visitor_user", "reader_user"]


def instance_to_model_info(model_instance: Model, data_cls: Type) -> object:
    instance = data_cls()

    for field_name in instance.__dict__.keys():
        val = getattr(model_instance, field_name, UNSET)
        if isinstance(model_instance._meta.get_field(field_name), ManyToManyField):
            val = val.all()

        setattr(instance, field_name, val)

    return instance


def test_model_info_and_model_instance(
    model_instance, model_info, ignore_value: Sequence[str] = ()
):
    for field_name, target_value in model_info.__dict__.items():
        if field_name in ignore_value:
            continue
        if target_value is UNSET:
            continue

        field_value = getattr(model_instance, field_name)
        if isinstance(field_value, Model):
            assert hasattr(target_value, "id")
            target_value = field_value.__class__.objects.get(id=target_value.id)
        elif isinstance(model_instance._meta.get_field(field_name), ManyToManyField):
            field_value = set(field_value.all())
            target_value = {
                target_item
                if isinstance(target_item, Model)
                else target_item._django_type.model.objects.get(id=target_item.id)
                for target_item in target_value
            }

        assert (
            field_value == target_value
        ), f"{field_name} is {field_value} instead of {target_value}"


def bridge_test_helper(
    bridge_cls: Type[DataBridgeBase],
    new_model_info,
    old_model_info=None,
    request: HttpRequest = None,
    min_user_role: int | UserRoles = -1,
) -> None:
    user: User = request and request.user
    bridged_model: Type[Model] | None = bridge_cls.bridged_model
    assert bridged_model is not None

    if min_user_role >= 0 and user.role < min_user_role:
        with pytest.raises(ValidationError):
            bridge_cls.bridges_from_model_info(old_model_info, request=request)
        instance = bridged_model.objects.get(id=new_model_info.id)
        assert old_model_info is not None
        test_model_info_and_model_instance(instance, old_model_info)
    else:
        bridge_cls.bridges_from_model_info(new_model_info, request=request)
        try:
            instance = bridged_model.objects.get(id=old_model_info.id)
        except bridged_model.DoesNotExist:
            attaching_to: Tuple[str] = bridge_cls.attaching_to
            assert attaching_to is not None, "model instance not found"
            for attaching_to_field in attaching_to:
                assert (
                    getattr(new_model_info, attaching_to_field) is UNSET
                ), f"{attaching_to} is empty, but {bridged_model} still exists"
        else:
            test_model_info_and_model_instance(instance, new_model_info)
