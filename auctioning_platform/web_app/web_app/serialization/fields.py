from marshmallow import exceptions, fields

from foundation.value_objects.factories import get_dollars


class Dollars(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):  # type: ignore
        """
        Serialize the value to string.

        Args:
            self: (todo): write your description
            value: (todo): write your description
            attr: (todo): write your description
            obj: (todo): write your description
        """
        return str(value)

    def _deserialize(self, value, attr, data, **kwargs):  # type: ignore
        """
        Deserialize value into a : class.

        Args:
            self: (todo): write your description
            value: (str): write your description
            attr: (todo): write your description
            data: (todo): write your description
        """
        try:
            return get_dollars(value)
        except ValueError as exc:
            raise exceptions.ValidationError(str(exc))
