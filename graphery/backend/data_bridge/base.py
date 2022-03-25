from __future__ import annotations

from django.db.models.options import Options
from types import FunctionType

from typing import Type, Optional, Final, TypeVar, Dict, Generic, Tuple

from django.db.models import Model, Field, ForeignObjectRel

MODEL_TYPE = TypeVar("MODEL_TYPE", bound=Model)

__all__ = ["DataBridgeMeta", "DataBridgeBase", "DataBridgeProtocol"]


class DataBridgeMeta(type, Generic[MODEL_TYPE]):
    __bridged_model_name: Final[str] = "_bridged_model"
    __bridge_prefix: Final[str] = "_bridges_"
    __bridge_prefix_len: Final[int] = len(__bridge_prefix)
    __bridge_storage_name: Final[str] = "_bridges"
    # member attr
    _bridged_model: Final[Optional[Type[MODEL_TYPE]]] = None
    _bridges: Final[dict[str, FunctionType]] = None

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
                isinstance(
                    fn := getattr(new_class, name), FunctionType
                )  # TODO: or is it method type?
                and name.startswith(mcs.__bridge_prefix)
            )
        }

        bridged_model = getattr(new_class, mcs.__bridged_model_name, None)

        if bridged_model is None:
            import warnings

            warnings.warn(
                f"No model was defined for this bridge {new_class}, {mcs.__bridged_model_name}."
            )
        else:
            meta: Options = bridged_model._meta
            if meta.abstract:
                raise ValueError(f"Cannot bridge abstract model {bridged_model}.")
            dict_of_fields: Dict[str, FunctionType] = {
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
    pass


class DataBridgeBase(DataBridgeProtocol, Generic[MODEL_TYPE]):
    def __init__(self, model_instance: MODEL_TYPE) -> None:
        self.model_instance = model_instance
