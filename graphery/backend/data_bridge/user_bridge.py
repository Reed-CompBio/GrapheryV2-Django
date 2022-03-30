from __future__ import annotations

import re
from django.core.validators import validate_email

from typing import final

from django.http import HttpRequest
from strawberry.arguments import UNSET
from strawberry_django.legacy.mutations import auth

from . import DataBridgeBase, ValidationError
from ..models import User
from ..types import UserMutationType


__all__ = ["UserBridge"]


class UserBridge(DataBridgeBase[User, UserMutationType]):
    _bridged_model = User
    _custom_fields = ["new_password"]

    def bridges_model_info(
        self, model_info: UserMutationType, *, request: HttpRequest = None, **kwargs
    ) -> UserBridge[User, UserMutationType]:
        self._can_bridge()

        if request is None:
            return self

        user = request.user
        if not user.is_authenticated:
            # if it's not authenticated, we can't do anything
            raise ValidationError("User is not authenticated")

        if user.id != self._model_instance.id:
            # if it's not the same user, we can't do anything
            raise ValidationError("User is not authorized")

        if model_info.new_password is not UNSET:
            # check if the user is trying to change the password
            self._bridges_new_password(
                model_info.new_password, model_info.password, request=request
            )
        elif model_info.password is not UNSET:
            # check if the user is trying to change the password
            raise ValidationError(
                "Submit new password to change the password, otherwise leave it empty"
            )
        else:
            # just update the user info
            super().bridges_model_info(model_info, request=request, **kwargs)

        return self

    def _has_basic_permission(
        self, request: HttpRequest, error_msg: str = None
    ) -> None:
        """
        :param request:
        :param error_msg:
        :return:
        """
        super(UserBridge, self)._has_basic_permission(request, error_msg)
        if not (
            request.user.is_authenticated and request.user.id == self._model_instance.id
        ):
            raise ValidationError(error_msg or self._default_permission_error_msg)

    @final
    def _bridges_new_password(
        self,
        new_password: str,
        old_password: str | UNSET,
        *_,
        request: HttpRequest = None,
        **__,
    ) -> None:
        """
        This method is called when the user is trying to change the password
        :param new_password:
        :param old_password:
        :param args:
        :param kwargs:
        :return:
        """
        self._has_basic_permission(
            request, "Cannot change password without authentication"
        )

        if old_password is UNSET:
            raise ValidationError("Old password is required to change to the new one")

        auth_user = auth.authenticate(
            username=self._model_instance.username, password=old_password
        )
        if auth_user and auth_user.id == self._model_instance.id:
            self._model_instance.set_password(new_password)
            self._model_instance.save()
        else:
            raise ValidationError("Old password is incorrect")

    @final
    def _bridges_password(self, *args, **kwargs) -> None:
        """
        This method is left empty because _bridges_new_password() is used instead
        :param args:
        :param kwargs:
        :return:
        """
        raise ValidationError("This method is not allowed to be called")

    __username_regex: re.Pattern = re.compile(
        r"^(?=.{8,20}$)(?![\d_])(?!.*[_]{2})[\w]+(?<![_])$"
    )

    def _bridges_username(
        self, username: str, *_, request: HttpRequest = None, **__
    ) -> None:
        """
        :param args:
        :param kwargs:
        :return:
        """
        self._has_basic_permission(
            request, "Cannot change username without authentication"
        )

        username = username.strip()
        if not self.__username_regex.match(username):
            # TODO detailed error diagnostics and messages
            raise ValidationError("Username is not valid")

        self._model_instance.username = username
        self._model_instance.save()

    def _bridges_email(self, email: str, *_, request: HttpRequest = None, **__) -> None:
        """
        :param args:
        :param kwargs:
        :return:
        """
        self._has_basic_permission(
            request, "Cannot change email without authentication"
        )

        email = email.strip()
        validate_email(email)

        self._model_instance.email = email
        self._model_instance.save()

    def _bridges_displayed_name(
        self, displayed_name: str, *_, request: HttpRequest = None, **__
    ) -> None:
        """
        :param args:
        :param kwargs:
        :return:
        """
        self._has_basic_permission(
            request, "Cannot change displayed name without authentication"
        )

        displayed_name = displayed_name.strip()

        self._model_instance.displayed_name = displayed_name
        self._model_instance.save()

    def _bridges_in_mailing_list(
        self, in_mailing_list: bool, *_, request: HttpRequest = None, **__
    ) -> None:
        """
        :param in_mailing_list:
        :param args:
        :param request:
        :param kwargs:
        :return:
        """
        self._has_basic_permission(
            request, "Cannot change in_mailing_list without authentication"
        )

        in_mailing_list = bool(in_mailing_list)

        self._model_instance.in_mailing_list = in_mailing_list
        self._model_instance.save()
