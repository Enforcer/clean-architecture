from dataclasses import dataclass
import uuid


@dataclass
class Address:
    uuid: uuid.UUID
    street: str
    house_number: str
    city: str
    state: str
    zip_code: str
    country: str
