from typing import Type, TypeVar, cast

from flask import Request, abort, jsonify, make_response
from marshmallow import Schema, exceptions
from marshmallow_dataclass import class_schema

from foundation.value_objects import Money

from web_app.serialization.fields import Dollars

TDto = TypeVar("TDto")


class BaseSchema(Schema):
    TYPE_MAPPING = {Money: Dollars}


def get_dto(request: Request, dto_cls: Type[TDto], context: dict) -> TDto:
    schema_cls = class_schema(dto_cls, base_schema=BaseSchema)
    schema = schema_cls()
    try:
        return cast(TDto, schema.load(dict(context, **request.json)))
    except exceptions.ValidationError as exc:
        abort(make_response(jsonify(exc.messages), 400))
