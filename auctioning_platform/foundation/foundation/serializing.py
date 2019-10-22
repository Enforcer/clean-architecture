import dataclasses
from datetime import datetime
from enum import Enum
import json
from typing import Dict, Tuple, Type, TypeVar
from uuid import UUID

from typing_extensions import Protocol

from foundation.value_objects import Money
from foundation.value_objects.factories import get_dollars

T = TypeVar("T")


class Dataclass(Protocol):
    # as already noted in comments, checking for this attribute is currently
    # the most reliable way to ascertain that something is a dataclass
    __dataclass_fields__: Dict


def _extract_type_if_optional(type_hint: Type) -> Tuple[Type, bool]:
    if hasattr(type_hint, "__args__") and type(None) in type_hint.__args__:
        return type_hint.__args__[0], True
    elif type_hint in serializers and type_hint in deserializers:
        return type_hint, False
    else:
        raise Exception(f"Jeszcze tego nie ogarniam - {type_hint}")


def _deserialize_dt(raw_dt: str) -> datetime:
    try:
        return datetime.strptime(raw_dt, "%Y-%m-%dT%H:%M:%S.%f%z")  # with tz info
    except ValueError:
        return datetime.strptime(raw_dt, "%Y-%m-%dT%H:%M:%S.%f")  # naive


deserializers = {
    int: int,
    str: str,
    datetime: _deserialize_dt,
    Money: lambda dict_repr: get_dollars(dict_repr["amount"]),
    UUID: UUID,
}


serializers = {
    int: int,
    str: str,
    datetime: lambda dt: dt.strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
    Money: lambda money: {"amount": str(money.amount), "currency": money.currency.iso_code},
    UUID: str,
}


def from_json(json_repr: dict, dataclass: Type[T]) -> T:
    data = {}
    for field in dataclasses.fields(dataclass):
        field_type, _ = _extract_type_if_optional(field.type)
        if field_type not in deserializers:
            if issubclass(field_type, Enum):
                deserializers[field_type] = field_type
            else:
                raise Exception(f"Type {field_type} not supported")

        if json_repr[field.name]:
            data[field.name] = deserializers[field_type](json_repr[field.name])  # type: ignore
        else:
            data[field.name] = None

    return dataclass(**data)  # type: ignore


def to_json(dataclass_instance: Dataclass) -> str:
    data = {}
    for field in dataclasses.fields(type(dataclass_instance)):
        field_type, _ = _extract_type_if_optional(field.type)
        if field_type not in serializers:
            if issubclass(field_type, Enum):
                serializers[field_type] = lambda field: field.value
            else:
                raise Exception(f"Type {field_type} not supported")

        if getattr(dataclass_instance, field.name):
            data[field.name] = serializers[field_type](getattr(dataclass_instance, field.name))  # type: ignore
        else:
            data[field.name] = None

    return json.dumps(data)
