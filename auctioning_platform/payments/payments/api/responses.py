from dataclasses import dataclass, fields


@dataclass
class Response:
    @classmethod
    def from_dict(cls, data: dict) -> "Response":
        cls_fields = fields(cls)
        matching_data = {field.name: data[field.name] for field in cls_fields}
        return cls(**matching_data)  # type: ignore


@dataclass
class ChargeResponse(Response):
    id: str


@dataclass
class CaptureResponse(Response):
    pass
