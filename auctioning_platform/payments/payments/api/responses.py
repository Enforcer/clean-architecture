from dataclasses import dataclass, fields


@dataclass
class Response:
    @classmethod
    def from_dict(cls, data: dict) -> "Response":
        """
        Create a : class from a dictionary.

        Args:
            cls: (todo): write your description
            data: (array): write your description
        """
        cls_fields = fields(cls)
        matching_data = {field.name: data[field.name] for field in cls_fields}
        return cls(**matching_data)  # type: ignore


@dataclass
class ChargeResponse(Response):
    id: str


@dataclass
class CaptureResponse(Response):
    pass
