from __future__ import annotations

import json
from functools import wraps

from django.core.exceptions import ValidationError as _ValidationError
from django.db import transaction
from django.db.models.fields.related import RelatedField
from django.db.transaction import Atomic
from django.http import HttpRequest
from strawberry import UNSET
from uuid import UUID

from django.db.models.options import Options

from typing import (
    Type,
    Optional,
    Final,
    TypeVar,
    Dict,
    Generic,
    Tuple,
    ClassVar,  # https://youtrack.jetbrains.com/issue/PY-20811
    Callable,
    ParamSpec,
    List,
    overload,
    Protocol,
)

from django.db.models import Model, Field, ForeignObjectRel
from strawberry.types import Info

from ..models import (
    LangCode,
    Status,
    StatusMixin,
    LangMixin,
    UUIDMixin,
    MixinBase,
    UserRoles,
    User,
    WRITER_ALLOWED_STATUS,
)
from ..types import OperationType

MODEL_TYPE = TypeVar("MODEL_TYPE", bound=Model)

_P = ParamSpec("_P")
_T = TypeVar("_T")

__all__ = [
    "ValidationError",
    "text_processing_wrapper",
    "json_validation_wrapper",
    "DataBridgeProtocol",
    "DataBridgeBase",
    "MODEL_TYPE",
    "DATA_TYPE",
    "DATA_BRIDGE_TYPE",
    "FAKE_UUID",
]

ValidationError = _ValidationError


def basic_permission_validator_wrapper(perm_error_txt: str = None) -> Callable:
    """
    a wrapper validates the basic permission before passing it to the function
    :param perm_error_txt: error message when getting permission error
    :return: the wrapped function to wrap bridge functions
    """

    def _wrapper_helper(fn: Callable) -> Callable:
        @wraps(fn)
        def _wrapper(
            self: DataBridgeBase,
            *args,
            request: HttpRequest = None,
            **kwargs: _HP.kwargs,
        ) -> _HT:
            self._has_basic_permission(
                request, perm_error_txt or self._default_permission_error_msg
            )

            return fn(self, *args, request=request, **kwargs)

        return _wrapper

    return _wrapper_helper


def bridges_uuid_mixin(cls: Type[DATA_BRIDGE_TYPE]) -> Type[DATA_BRIDGE_TYPE]:
    def _bridges_id(*_, **__) -> None:
        """
        Bridges the id of the model, which is doing nothing.
        since the id is already set.
        :param args:
        :param kwargs:
        :return:
        """
        return None

    setattr(cls, "_bridges_id", _bridges_id)

    return cls


def bridges_status_mixin(cls: Type[DATA_BRIDGE_TYPE]) -> Type[DATA_BRIDGE_TYPE]:
    """
    data bridge mixin for status, serving as a decorator
    this function injects item_status bridge function to the data bridge
    :param cls:
    :return:
    """

    def _bridges_item_status(
        self, status: str, *_, request: HttpRequest = None, **__
    ) -> None:
        try:
            item_status: Status = Status(status)
        except ValueError:
            raise ValueError(f"{status} is not a valid status.")

        # some item status cannot be set by every one
        user: User = request.user if request else None

        if user and user.role >= UserRoles.EDITOR:
            pass
        elif user and user.role >= UserRoles.TRANSLATOR:
            if item_status not in WRITER_ALLOWED_STATUS:
                raise ValidationError(
                    f"You don't have the permission to set '{item_status}' status."
                )
        else:
            raise ValidationError("You don't have the permission to edit item status")

        self._model_instance.item_status = item_status

    setattr(cls, "_bridges_item_status", _bridges_item_status)

    return cls


def bridges_lang_mixin(cls: Type[DATA_BRIDGE_TYPE]) -> Type[DATA_BRIDGE_TYPE]:
    """
    data bridge mixin for lang, serving as a decorator
    this function injects item_lang bridge function to the data bridge
    :param cls:
    :return:
    """

    def _bridges_lang_code(self, lang_code: str, *_, **__) -> None:
        try:
            lang = LangCode(lang_code)
        except ValueError:
            raise ValidationError(f"{lang_code} is not a valid language code")

        self._model_instance.lang_code = lang

    setattr(cls, "_bridges_lang_code", _bridges_lang_code)

    return cls


_HP = ParamSpec("_HP")
_HT = TypeVar("_HT")


def attaching_bridge_fn_wrapper(fn: Callable[_HP, _HT]) -> Callable[_HP, _HT | UNSET]:
    """
    wrapper for fields specified in `attaching_to`
    :param fn: the field bridge function
    :return: the wrapped bridge function
    """

    @wraps(fn)
    def _wrapper(*args: _HP.args, **kwargs: _HP.kwargs) -> _HT | UNSET:
        self, required_arg, *optional_arg = args
        if required_arg is UNSET:
            self.delete_model_instance(**kwargs)
            return UNSET
        else:
            return fn(*args, **kwargs)

    return _wrapper


def text_processing_wrapper(*, arg_num: int = 1) -> Callable[[Callable], Callable]:
    """
    generate a wrapper for a function that takes a text argument
    based on the specified number of arguments
    :param arg_num:
    :return:
    """

    def _wrapper_helper(fn: Callable[_HP, _HT]) -> Callable[_HP, _HT]:
        """
        wraps the function such that the first `arg_num` str arguments are stripped
        :param fn:
        :return:
        """

        @wraps(fn)
        def _wrapper(self: DataBridgeBase, *args, **kwargs: _HP.kwargs) -> _HT:
            text_args, other_args = args[:arg_num], args[arg_num:]

            processed_text_args = [
                text_arg.strip() if isinstance(text_arg, str) else text_arg
                for text_arg in text_args
            ]

            return fn(self, *processed_text_args, *other_args, **kwargs)

        return _wrapper

    return _wrapper_helper


def json_validation_wrapper(fn: Callable) -> Callable:
    """
    a wrapper validates the JSON data before passing it to the function
    :param fn: the bridge function
    :return: the wrapped bridge function
    """

    @wraps(fn)
    def _wrapper(self: DataBridgeBase, *args, **kwargs: _HP.kwargs) -> _HT:
        json_content, *args = args

        try:
            if isinstance(json_content, str):
                json_content = json.loads(json_content)
            elif isinstance(json_content, Dict):
                json.dumps(json_content)
        except json.JSONDecodeError:
            raise ValidationError(
                f"result_json is not valid JSON, but got {json_content}"
            )

        return fn(self, json_content, *args, **kwargs)

    return _wrapper


class DataBridgeMeta(type, Generic[MODEL_TYPE]):
    """
    Metaclass for DataBridge.
    A DataBridge class implements functions whose names start with `__bridge_prefix`,
    in this case, the prefix is `_bridges_`. The string segment after the prefix is
    the name of the field in the model specified in `__bridged_model_name`, which is
    `_bridged_model`. The function pipes data from input to the field in the model
    with necessary, custom checking and processing. The return value for those
    functions is usually None.
    For example::

        def _bridges_id(self, value: UUID) -> None:
            # some checks to see if value is a valid UUID and
            # if it is, do something with it
            # if it's not, raise an ValidationError exception
            pass

    This metaclass collects those bridge functions and stores them in a dict as a
    class attribute named by `__bridge_storage_name`, which is `_bridges`.

    The signature of the bridge functions should follow the following format::

        def _bridges_<field_name>(
        self,
        [required_value: <data_type>, [required_value: <data_type>, [...]]]
        *args, [request: HttpRequest = None, ] **kwargs) -> <data_type>:

    bridge functions should not save the model instance

    """

    __bridged_model_cls_name: Final[str] = "_bridged_model_cls"
    __bridge_prefix: Final[str] = "_bridges_"
    __bridge_storage_name: Final[str] = "_bridges"
    __mixin_mapping: Dict[Type[MixinBase], Callable] = {
        UUIDMixin: bridges_uuid_mixin,
        StatusMixin: bridges_status_mixin,
        LangMixin: bridges_lang_mixin,
    }
    # member attr
    _custom_fields: List[str]
    _bridged_model_cls: Optional[Type[MODEL_TYPE]]
    _bridges: Optional[Dict[str, Callable[_P, _T]]]
    # controls over the bridge via model info
    _attaching_to: str | Tuple[str] | None

    @classmethod
    @property
    def __bridge_prefix_len(mcs):
        return len(mcs.__bridge_prefix)

    def __new__(mcs, name: str, bases: Tuple[Type], attrs: Dict):
        """
        Create a new DataBridge class with a give _bridged_model.
        :param name:
        :param bases:
        :param attrs:
        """
        new_class = super().__new__(mcs, name, bases, attrs)

        bridged_model: Type[Model] = getattr(
            new_class, mcs.__bridged_model_cls_name, None
        )

        if bridged_model is not None:
            model_bases = bridged_model.__bases__
            for mixin_cls, bridge_adder in mcs.__mixin_mapping.items():
                if mixin_cls in model_bases:
                    bridge_adder(new_class)

        defined_fn_mapping = {
            name[mcs.__bridge_prefix_len :]: fn
            for name in dir(new_class)
            if (
                isinstance(fn := getattr(new_class, name), Callable)
                and name.startswith(mcs.__bridge_prefix)
            )
        }

        if bridged_model is not None:
            meta: Options = bridged_model._meta

            if meta.abstract:
                raise ValueError(f"Cannot bridge abstract model {bridged_model}.")

            dict_of_fields: Dict[str, Callable] = {
                field.name: field
                for field in meta.get_fields()
                if isinstance(field, (Field, RelatedField, ForeignObjectRel))
            }

            if new_class._attaching_to is not None:
                if isinstance(new_class._attaching_to, str):
                    new_class._attaching_to = (new_class._attaching_to,)

                if not isinstance(new_class._attaching_to, Tuple):
                    raise TypeError("_attaching_to must be a tuple, str, or None")

                for field_name in new_class._attaching_to:
                    attaching_bridge_fn = defined_fn_mapping.get(field_name, None)
                    if attaching_bridge_fn is None:
                        raise ValueError(
                            f"Bridge function for attaching point {field_name} not found in {bridged_model}"
                        )

                    defined_fn_mapping[field_name] = attaching_bridge_fn_wrapper(
                        attaching_bridge_fn
                    )

            for field_name, fn in defined_fn_mapping.items():
                if (dict_of_fields.get(field_name, None)) is None:
                    if field_name not in new_class._custom_fields:
                        raise ValueError(
                            f"Field `{field_name}` ({[defined_fn_mapping.keys()]}) not found in {bridged_model}"
                        )

                defined_fn_mapping[field_name] = basic_permission_validator_wrapper(
                    f"You do not have the permission to edit `{field_name}` in `{new_class.__name__}`"
                )(fn)

            new_class._bridges = defined_fn_mapping

        return new_class


class DataBridgeProtocol(metaclass=DataBridgeMeta[MODEL_TYPE]):
    __slots__ = ("_ident", "_model_instance", "_transaction_db")

    _custom_fields: ClassVar[List[str]] = []
    _bridged_model_cls: ClassVar[Optional[Type[MODEL_TYPE]]] = None
    _bridges: ClassVar[Optional[Dict[str, Callable[_P, _T]]]] = None
    _attaching_to: ClassVar[Optional[Tuple[str]]] = None

    _ident: Optional[UUID]
    _model_instance: Optional[MODEL_TYPE]
    _transaction_db: Optional[Atomic]

    _require_edit_authentication: ClassVar[bool] = False
    _minimal_edit_user_role: ClassVar[UserRoles] = UserRoles.READER
    _require_delete_authentication: ClassVar[bool] = True
    _minimal_delete_user_role: ClassVar[UserRoles] = UserRoles.EDITOR

    @classmethod
    @property
    def bridged_model_cls(cls) -> Optional[Type[MODEL_TYPE]]:
        return cls._bridged_model_cls

    @classmethod
    @property
    def custom_fields(cls) -> List[str]:
        return cls._custom_fields

    @classmethod
    @property
    def attaching_to(cls) -> Optional[Tuple[str]]:
        return cls._attaching_to

    @classmethod
    @property
    def require_edit_authentication(cls) -> bool:
        return cls._require_edit_authentication

    @classmethod
    @property
    def require_delete_authentication(cls) -> bool:
        return cls._require_delete_authentication

    @classmethod
    @property
    def minimal_edit_user_role(cls) -> UserRoles:
        return cls._minimal_edit_user_role

    @classmethod
    @property
    def minimal_delete_user_role(cls) -> UserRoles:
        return cls._minimal_delete_user_role

    @property
    def model_instance(self) -> MODEL_TYPE:
        return self._model_instance


DATA_BRIDGE_TYPE = TypeVar("DATA_BRIDGE_TYPE", bound="DataBridgeBase")
DATA_TYPE = TypeVar("DATA_TYPE")
FAKE_UUID: Final[UUID] = UUID("00000000-0000-0000-0000-000000000000")


class _OperationFn(Protocol):
    def __call__(
        self: Type[DATA_BRIDGE_TYPE],
        bridge_instance: DATA_BRIDGE_TYPE,
        model_info: DATA_TYPE,
        *,
        request: Optional[HttpRequest] = None,
        **kwargs,
    ):
        ...


class DataBridgeBase(DataBridgeProtocol, Generic[MODEL_TYPE, DATA_TYPE]):
    """
    Base class for data bridges.
    """

    __slots__ = ("_ident", "_model_instance", "_transaction_db")

    def __init__(self, ident: str | UUID | UNSET) -> None:
        """
        Create a new DataBridge instance with uuid.
        :param ident: uuid instance or string
        """
        # raise error if there is no bridged model
        if self._bridged_model_cls is None:
            raise ValueError(f"No model was defined for this bridge {self.__class__}")
        # setup UUID, raise an error if it is not valid
        self._ident: Optional[UUID] = UUID(ident) if isinstance(ident, str) else ident
        if not isinstance(self._ident, UUID) and self._ident is not UNSET:
            raise TypeError(
                f"{self.__class__.__name__} ident must be a UUID, a UUID string, or UNSET, but got {type(self._ident)}."
            )

        # setup model instance
        self._model_instance: Optional[MODEL_TYPE] = None
        self._transaction_db: Optional[Atomic] = None

    def delete_model_instance(self, *, request: HttpRequest = None, **kwargs) -> None:
        """
        Delete the model instance.
        :return:
        """
        self._has_delete_permission(request, **kwargs)
        if self._model_instance is None:
            raise ValueError(f"{self.__class__.__name__} model instance is not set.")
        self._model_instance.delete()
        self._model_instance = None
        self._ident = None

    def __enter__(self) -> DATA_BRIDGE_TYPE:
        """
        Support db transaction so that everything will be rolled back if an error occurs.
        :return:
        """
        self._transaction_db = transaction.atomic()
        self._transaction_db.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Support db transaction so that everything will be rolled back if an error occurs.
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        self._transaction_db.__exit__(exc_type, exc_val, exc_tb)
        self._transaction_db = None

    def _is_in_transaction(self) -> bool:
        """
        check if the bridge is in a transaction.
        :return:
        """
        return self._transaction_db is not None and isinstance(
            self._transaction_db, Atomic
        )

    def get_instance(self) -> DATA_BRIDGE_TYPE:
        """
        Get the model instance for this bridge.
        Querying with FAKE UUID means the model will be created
        otherwise it will be retrieved from the database.
        :return: DataBridge instance for chained method calls.
        """
        if self._ident is UNSET or self._ident == FAKE_UUID:
            self._model_instance = self._bridged_model_cls()
        else:
            self._model_instance = self._bridged_model_cls.objects.get(pk=self._ident)
        return self

    def _can_bridge(self) -> None:
        """
        check if the model instance is valid for bridging.
        :return:
        """
        # raise error if there is no bridged model instance
        if self._model_instance is None or not isinstance(
            self._model_instance, self._bridged_model_cls
        ):
            raise ValueError(f"{self.__class__.__name__} instance is not initialized.")
        # raise error if bridging is not in transaction
        if not self._is_in_transaction():
            raise ValueError(
                f"{self.__class__.__name__} instance is not in a transaction."
            )

    @overload
    def bridges_field(
        self, field_name: str, *args, request: HttpRequest, **kwargs
    ) -> _T:
        ...

    def bridges_field(
        self,
        field_name: str,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _T:
        """
        Bridges data to the model.
        :param field_name: the field to which the data will be bridged.
        :param args: arguments to pass to the bridged function.
        :param kwargs: keyword arguments to pass to the bridged function.
        :return: the result of the bridged function.
        """
        self._can_bridge()
        return self._bridge_field(field_name, *args, **kwargs)

    def _bridge_field(self, field_name: str, *args, **kwargs) -> _T:
        """
        bridge a single field to the model.
        :param field_name: the name of the field
        :param args: arguments to pass to the bridged function.
        :param kwargs: keyword arguments to pass to the bridged function.
        :return:
        """
        bridge_fn = self._bridges.get(field_name, None)
        if bridge_fn is None:
            raise ValueError(
                f"{self.__class__.__name__} has no bridge for {field_name}."
            )

        res = bridge_fn(self, *args, **kwargs)

        self.save()

        return res

    @overload
    def bridges_model_info(
        self, model_info: DATA_TYPE, *, request: HttpRequest, **kwargs
    ) -> DATA_BRIDGE_TYPE:
        ...

    def bridges_model_info(self, model_info: DATA_TYPE, **kwargs) -> DATA_BRIDGE_TYPE:
        """
        Bridges the model info to the model if the piece of data exists.
        To use this function, the bridge must be in a transaction.
        :param model_info:
        :return:
        """
        self._can_bridge()
        if self._attaching_to is not None:
            for _attaching_to_field in self._attaching_to:
                if getattr(model_info, _attaching_to_field) is UNSET:
                    self._bridge_field(
                        _attaching_to_field,
                        UNSET,
                        **kwargs,
                    )
                    return self

        for field_name, bridge_fn in self._bridges.items():
            if (field_value := getattr(model_info, field_name, UNSET)) is not UNSET:
                bridge_fn(self, field_value, **kwargs)

        self.save()

        return self

    def save(self):
        if self._model_instance:
            self._model_instance.save()

    @classmethod
    def bridges_from_model_info(
        cls, model_info: DATA_TYPE, *, request: HttpRequest = None, **kwargs
    ) -> DATA_BRIDGE_TYPE:
        """
        Create a new DataBridge instance from a model info.
        The model info must contain the id of the model.
        :param model_info:
        :param request:
        :return:
        """
        with cls(model_info.id).get_instance() as data_bridge:  # type: DATA_BRIDGE_TYPE
            data_bridge.bridges_model_info(model_info, request=request, **kwargs)

        return data_bridge

    @classmethod
    def _delete_op(
        cls,
        bridge_instance: DATA_BRIDGE_TYPE,
        model_info: DATA_TYPE,
        *,
        request: Optional[HttpRequest] = None,
        **kwargs,
    ):
        bridge_instance.delete_model_instance(request=request, **kwargs)

    @classmethod
    def _create_op(
        cls,
        bridge_instance: DATA_BRIDGE_TYPE,
        model_info: DATA_TYPE,
        *,
        request: Optional[HttpRequest] = None,
        **kwargs,
    ):
        if cls.bridged_model_cls.objects.filter(
            id=bridge_instance.model_instance.id
        ).exists():
            raise ValidationError(
                f'"{cls.bridged_model_cls.__name__}" Model instance with id "{bridge_instance.model_instance.id}" '
                f"already exists and cannot be created again."
            )
        else:
            bridge_instance.bridges_model_info(model_info, request=request, **kwargs)

    @classmethod
    def _update_op(
        cls,
        bridge_instance: DATA_BRIDGE_TYPE,
        model_info: DATA_TYPE,
        *,
        request: Optional[HttpRequest] = None,
        **kwargs,
    ):
        if cls.bridged_model_cls.objects.filter(
            id=bridge_instance.model_instance.id
        ).exists():
            bridge_instance.bridges_model_info(model_info, request=request, **kwargs)
        else:
            raise ValidationError(
                f"{cls.bridged_model_cls.__name__} Model does not exist and cannot be updated."
            )

    @classmethod
    def bridges_from_mutation(
        cls,
        op: OperationType,
        model_info: DATA_TYPE,
        *,
        info: Info | None = None,
        **kwargs,
    ) -> Optional[DATA_BRIDGE_TYPE]:
        """
        Create a new DataBridge instance from a mutation.
        The mutation must contain the id of the model.
        :param op:
        :param model_info:
        :param info: strawberry info
        :return:
        """
        request: HttpRequest | None = info.context.request if info else None

        with cls(model_info.id).get_instance() as data_bridge:  # type: DataBridgeBase
            op_fn: _OperationFn = getattr(cls, f"_{op.value}_op", None)
            if op_fn is None:
                raise RuntimeError(f'"{op}" is not a defined operation.')

            op_fn(data_bridge, model_info, request=request, **kwargs)

        return data_bridge.model_instance

    @property
    def _default_permission_error_msg(self) -> str:
        return f"You do not have permission to perform this action in {self.__class__.__name__}"

    def _has_basic_permission(
        self, request: HttpRequest, error_msg: str = None
    ) -> None:
        """
        Check if the user has permission to perform the action.
        the user must have the permission indicated in the _minimal_edit_user_role
        if they don't, an ValidationError is raised, with the message given in
        error_msg or _default_permission_error_msg if not given.
        :param request:
        :param error_msg:
        :return:
        """
        if self._require_edit_authentication:
            user: User = request.user
            if not user.is_authenticated:
                raise ValidationError("You must be logged in to perform this action.")
            if not (user.role >= self._minimal_edit_user_role):
                raise ValidationError(error_msg or self._default_permission_error_msg)

    def _has_delete_permission(
        self, request: HttpRequest, error_msg: str = None, **kwargs
    ) -> None:
        """
        Check if the user has permission to delete the model instance.
        the user must have the permission indicated in the _minimal_delete_user_role
        if they don't, an ValidationError is raised, with the message given in
        error_msg or _default_permission_error_msg if not given.
        :param request:
        :param error_msg:
        :param kwargs:
        :return:
        """
        if self._require_delete_authentication:
            user: User = request.user
            if not user.is_authenticated:
                raise ValidationError("You must be logged in to perform this action.")
            if not (user.role >= self._minimal_delete_user_role):
                raise ValidationError(error_msg or self._default_permission_error_msg)
