from typing import Type, TypeVar, cast

from flask import Request, abort, jsonify, make_response
from marshmallow import Schema, exceptions

TSchema = TypeVar("TSchema", bound=Schema)


def get_input_dto(request: Request, schema_cls: Type[TSchema], context: dict) -> TSchema:
    schema = schema_cls(context=context)
    try:
        return cast(TSchema, schema.load(request.json))
    except exceptions.ValidationError as exc:
        abort(make_response(jsonify(exc.messages), 400))
