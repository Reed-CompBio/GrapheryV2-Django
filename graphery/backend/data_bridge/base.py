from __future__ import annotations

from django.core.exceptions import ValidationError as _ValidationError
from django.db import transaction
from django.db.models.fields.related import RelatedField
from django.db.transaction import Atomic
from django.http import HttpRequest
from strawberry.arguments import UNSET
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
)

from django.db.models import Model, Field, ForeignObjectRel

from ..models import LangCode, Status, StatusMixin, LangMixin, UUIDMixin, MixinBase

MODEL_TYPE = TypeVar("MODEL_TYPE", bound=Model)

_P = ParamSpec("_P")
_T = TypeVar("_T")

__all__ = [
    "ValidationError",
    "DataBridgeProtocol",
    "DataBridgeBase",
    "MODEL_TYPE",
    "DATA_TYPE",
    "DATA_BRIDGE_TYPE",
    "FAKE_UUID",
]

ValidationError = _ValidationError


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
    def _bridges_item_status(
        self, status: str, *_, request: HttpRequest = None, **__
    ) -> None:
        self._has_basic_permission(request)

        try:
            item_status: Status = Status(status)
        except ValueError:
            raise ValueError(f"{status} is not a valid status.")

        self._model_instance.item_status = item_status
        self._model_instance.save()

    setattr(cls, "_bridges_item_status", _bridges_item_status)

    return cls


def bridges_lang_mixin(cls: Type[DATA_BRIDGE_TYPE]) -> Type[DATA_BRIDGE_TYPE]:
    def _bridges_lang_code(
        self, lang_code: str, *_, request: HttpRequest = None, **__
    ) -> None:
        self._has_basic_permission(request)

        try:
            lang = LangCode(lang_code)
        except ValueError:
            raise ValidationError(f"{lang_code} is not a valid language code")

        self._model_instance.lang_code = lang
        self._model_instance.save()

    setattr(cls, "_bridges_lang_code", _bridges_lang_code)

    return cls


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

    """

    __bridged_model_name: Final[str] = "_bridged_model"
    __bridge_prefix: Final[str] = "_bridges_"
    __bridge_storage_name: Final[str] = "_bridges"
    __mixin_mapping: Dict[Type[MixinBase], Callable] = {
        UUIDMixin: bridges_uuid_mixin,
        StatusMixin: bridges_status_mixin,
        LangMixin: bridges_lang_mixin,
    }
    # member attr
    _custom_fields: List[str] = []
    _bridged_model: Optional[Type[MODEL_TYPE]] = None
    _bridges: Optional[Dict[str, Callable[_P, _T]]] = None

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

        bridged_model: Type[Model] = getattr(new_class, mcs.__bridged_model_name, None)

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
            for field_name, fn in defined_fn_mapping.items():
                if (dict_of_fields.get(field_name, None)) is None:
                    if field_name not in new_class._custom_fields:
                        raise ValueError(
                            f"Field {field_name} not found in {bridged_model}"
                        )

            new_class._bridges = defined_fn_mapping

        return new_class


class DataBridgeProtocol(metaclass=DataBridgeMeta[MODEL_TYPE]):
    _custom_fields: ClassVar[List[str]] = []
    _bridged_model: ClassVar[Optional[Type[MODEL_TYPE]]]
    _bridges: ClassVar[Optional[Dict[str, Callable[_P, _T]]]]

    _ident: Optional[UUID]
    _model_instance: Optional[MODEL_TYPE]
    _transaction_db: Optional[Atomic]


DATA_BRIDGE_TYPE = TypeVar("DATA_BRIDGE_TYPE", bound="DataBridgeBase")
DATA_TYPE = TypeVar("DATA_TYPE")
FAKE_UUID: Final[UUID] = UUID("00000000-0000-0000-0000-000000000000")


class DataBridgeBase(DataBridgeProtocol, Generic[MODEL_TYPE, DATA_TYPE]):
    def __init__(self, ident: str | UUID) -> None:
        """
        Create a new DataBridge instance with uuid.
        :param ident: uuid instance or string
        """
        # raise error if there is no bridged model
        if self._bridged_model is None:
            raise ValueError(f"No model was defined for this bridge {self.__class__}")
        # setup UUID, raise an error if it is not valid
        self._ident: Optional[UUID] = UUID(ident) if isinstance(ident, str) else ident
        if not isinstance(self._ident, UUID):
            raise TypeError(
                f"{self.__class__.__name__} ident must be a UUID or a UUID string."
            )

        # setup model instance
        self._model_instance: Optional[MODEL_TYPE] = None
        self._transaction_db: Optional[Atomic] = None

    def __enter__(self) -> DATA_BRIDGE_TYPE:
        self._transaction_db = transaction.atomic()
        self._transaction_db.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._transaction_db.__exit__(exc_type, exc_val, exc_tb)
        self._transaction_db = None

    def _is_in_transaction(self) -> bool:
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
        if self._ident == FAKE_UUID:
            self._model_instance = self._bridged_model()
        else:
            self._model_instance = self._bridged_model.objects.get(pk=self._ident)
        return self

    def _can_bridge(self) -> None:
        """
        check if the model instance is valid for bridging.
        :return:
        """
        # raise error if there is no bridged model instance
        if self._model_instance is None or not isinstance(
            self._model_instance, self._bridged_model
        ):
            raise ValueError(f"{self.__class__.__name__} instance is not initialized.")
        # raise error if bridging is not in transaction
        if not self._is_in_transaction():
            raise ValueError(
                f"{self.__class__.__name__} instance is not in a transaction."
            )

    def bridges(
        self,
        field_name: str,
        *args: _P.args,
        request: HttpRequest = None,
        **kwargs: _P.kwargs,
    ) -> _T:
        """
        Bridges data to the model.
        :param field_name: the field to which the data will be bridged.
        :param args: arguments to pass to the bridged function.
        :param request: the request object.
        :param kwargs: keyword arguments to pass to the bridged function.
        :return: the result of the bridged function.
        """
        self._can_bridge()
        bridge_fn = self._bridges.get(field_name, None)
        return bridge_fn(self, *args, request=request, **kwargs)

    def bridges_model_info(
        self, model_info: DATA_TYPE, *, request: HttpRequest = None, **kwargs
    ) -> DATA_BRIDGE_TYPE:
        """
        Bridges the model info to the model if the piece of data exists.
        :param model_info:
        :param request: HttpRequest instance if needed
        :return:
        """
        self._can_bridge()
        for field_name, bridge_fn in self._bridges.items():
            if (field_value := getattr(model_info, field_name, UNSET)) is not UNSET:
                bridge_fn(self, field_value, request=request)

        self._model_instance.save()

        return self

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
    @property
    def _default_permission_error_msg(cls) -> str:
        return f"You do not have permission to perform this action in {cls.__name__}"

    def _has_basic_permission(
        self, request: HttpRequest, error_msg: str = None
    ) -> None:
        return
