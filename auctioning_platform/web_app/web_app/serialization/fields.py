from marshmallow import exceptions, fields

from foundation.value_objects.factories import get_dollars


class Dollars(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):  # type: ignore
        return str(value)

    def _deserialize(self, value, attr, data, **kwargs):  # type: ignore
        try:
            return get_dollars(value)
        except ValueError as exc:
            raise exceptions.ValidationError(str(exc))
