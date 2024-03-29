from __future__ import annotations

import re
from django.core.validators import validate_email

from typing import final

from django.http import HttpRequest
from strawberry import UNSET
from django.contrib import auth

from . import DataBridgeBase, ValidationError, text_processing_wrapper
from ..models import User, UserRoles
from ..types import UserMutationType


__all__ = ["UserBridge"]


class UserBridge(DataBridgeBase[User, UserMutationType]):
    __slots__ = ()

    _bridged_model_cls = User
    _custom_fields = ["new_password"]

    _minimal_delete_user_role = UserRoles.ADMINISTRATOR
    _minimal_edit_user_role = UserRoles.ADMINISTRATOR

    def bridges_model_info(
        self, model_info: UserMutationType, *, request: HttpRequest = None, **kwargs
    ) -> UserBridge[User, UserMutationType]:
        self._can_bridge()

        if request is None:
            return self

        user: User = request.user
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

        self.save()

        return self

    def _has_basic_permission(
        self, request: HttpRequest, error_msg: str = None
    ) -> None:
        """
        :param request:
        :param error_msg:
        :return:
        """
        request_user: User = request.user
        if request_user == self._model_instance:
            return

        if not request_user.is_authenticated:
            raise ValidationError("You must be logged in to perform this action.")
        if not (request_user.role >= self._minimal_edit_user_role):
            raise ValidationError(error_msg or self._default_permission_error_msg)

    @final
    @text_processing_wrapper(arg_num=2)
    def _bridges_new_password(
        self,
        new_password: str,
        old_password: str | UNSET,
        *_,
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
        if old_password is UNSET:
            raise ValidationError("Old password is required to change to the new one")

        auth_user = auth.authenticate(
            username=self._model_instance.username, password=old_password
        )
        if auth_user and auth_user.id == self._model_instance.id:
            self._model_instance.set_password(new_password)
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

    @text_processing_wrapper()
    def _bridges_username(self, username: str, *_, **__) -> None:
        """
        :param args:
        :param kwargs:
        :return:
        """
        if not self.__username_regex.match(username):
            # TODO detailed error diagnostics and messages
            raise ValidationError("Username is not valid")

        self._model_instance.username = username

    @text_processing_wrapper()
    def _bridges_email(self, email: str, *_, **__) -> None:
        """
        :param args:
        :param kwargs:
        :return:
        """
        validate_email(email)

        self._model_instance.email = email

    @text_processing_wrapper()
    def _bridges_displayed_name(self, displayed_name: str, *_, **__) -> None:
        """
        :param args:
        :param kwargs:
        :return:
        """
        self._model_instance.displayed_name = displayed_name

    def _bridges_in_mailing_list(self, in_mailing_list: bool, *_, **__) -> None:
        """
        :param in_mailing_list:
        :param args:
        :param request:
        :param kwargs:
        :return:
        """
        in_mailing_list = bool(in_mailing_list)

        self._model_instance.in_mailing_list = in_mailing_list

    def _has_delete_permission(
        self, request: HttpRequest, error_msg: str = None, **kwargs
    ) -> None:
        request_user: User = request.user
        if request_user == self._model_instance:
            return

        if not request_user.is_authenticated:
            raise ValidationError("You must be logged in to perform this action.")
        if not (request_user.role >= self._minimal_delete_user_role):
            raise ValidationError(error_msg or self._default_permission_error_msg)
