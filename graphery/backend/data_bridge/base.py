from __future__ import annotations

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
    # ClassVar,  # https://youtrack.jetbrains.com/issue/PY-20811
    Callable,
    ParamSpec,
)

from django.db.models import Model, Field, ForeignObjectRel

MODEL_TYPE = TypeVar("MODEL_TYPE", bound=Model)

_P = ParamSpec("_P")
_T = TypeVar("_T")

__all__ = [
    "DataBridgeMeta",
    "DataBridgeProtocol",
    "DataBridgeBase",
    "MODEL_TYPE",
    "DATA_BRIDGE_TYPE",
    "FAKE_UUID",
]


class DataBridgeMeta(type, Generic[MODEL_TYPE]):
    __bridged_model_name: Final[str] = "_bridged_model"
    __bridge_prefix: Final[str] = "_bridges_"
    __bridge_prefix_len: Final[int] = len(__bridge_prefix)
    __bridge_storage_name: Final[str] = "_bridges"
    # member attr
    _bridged_model: Optional[Type[MODEL_TYPE]] = None
    _bridges: Optional[Dict[str, Callable[_P, _T]]] = None

    def __new__(mcs, name: str, bases: Tuple[Type], attrs: Dict):
        """
        Create a new DataBridge class with a give _bridged_model.
        :param name:
        :param bases:
        :param attrs:
        """
        new_class = super().__new__(mcs, name, bases, attrs)

        defined_fn_mapping = {
            name[mcs.__bridge_prefix_len :]: fn
            for name in new_class.__dict__
            if (
                isinstance(fn := getattr(new_class, name), Callable)
                and name.startswith(mcs.__bridge_prefix)
            )
        }

        bridged_model: Model = getattr(new_class, mcs.__bridged_model_name, None)

        if bridged_model is not None:
            meta: Options = bridged_model._meta
            if meta.abstract:
                raise ValueError(f"Cannot bridge abstract model {bridged_model}.")
            dict_of_fields: Dict[str, Callable] = {
                (
                    field.related_name
                    if isinstance(field, ForeignObjectRel)
                    else field.attname
                ): field
                for field in meta.get_fields()
                if isinstance(field, (Field, ForeignObjectRel))
            }
            for field_name, fn in defined_fn_mapping.items():
                if (dict_of_fields.get(field_name, None)) is None:
                    raise ValueError(f"Field {field_name} not found in {bridged_model}")

            new_class._bridges = defined_fn_mapping

        return new_class


class DataBridgeProtocol(metaclass=DataBridgeMeta[MODEL_TYPE]):
    _bridged_model: Optional[Type[MODEL_TYPE]]
    _bridges: Optional[Dict[str, Callable[_P, _T]]]


DATA_BRIDGE_TYPE = TypeVar("DATA_BRIDGE_TYPE", bound="DataBridgeBase")
FAKE_UUID: Final[UUID] = UUID("00000000-0000-0000-0000-000000000000")


class DataBridgeBase(DataBridgeProtocol, Generic[MODEL_TYPE]):
    def __init__(self, ident: str | UUID) -> None:
        """
        Create a new DataBridge instance with uuid.
        :param ident: uuid instance or string
        """
        # raise error if there is no bridged model
        if self._bridged_model is None:
            raise ValueError(f"No model was defined for this bridge {self.__class__}")
        # setup UUID, raise an error if it is not valid
        self._ident = UUID(ident) if isinstance(ident, str) else ident
        if not isinstance(self._ident, UUID):
            raise TypeError(
                f"{self.__class__.__name__} ident must be a UUID or a UUID string."
            )

        # setup model instance
        self._model_instance: Optional[MODEL_TYPE] = None

    def get_instance(self) -> DATA_BRIDGE_TYPE:
        """
        Get the model instance for this bridge.
        Querying with FAKE UUID means the model will be created
        otherwise it will be retrieved from the database.
        :return: DataBridge instance for chained method calls.
        """
        if self._ident == FAKE_UUID:
            self._model_instance = self._bridged_model()
            self._ident = self._model_instance.id
        else:
            self._model_instance = self._bridged_model.objects.get(pk=self._ident)
        return self

    def bridges(self, field_name: str, *args: _P.args, **kwargs: _P.kwargs) -> _T:
        """
        Bridges data to the model.
        :param field_name: the field to which the data will be bridged.
        :param args: arguments to pass to the bridged function.
        :param kwargs: keyword arguments to pass to the bridged function.
        :return: the result of the bridged function.
        """
        if (
            self._model_instance is None
            or self._ident == FAKE_UUID
            or not isinstance(self._model_instance, self._bridged_model)
        ):
            raise ValueError(
                f"{self.__class__.__name__} instance must be created before bridging data."
            )
        bridge_fn = self._bridges.get(field_name, None)
        return bridge_fn(self, *args, **kwargs)
