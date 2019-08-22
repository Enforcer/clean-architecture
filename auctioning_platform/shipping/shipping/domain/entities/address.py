from dataclasses import dataclass


@dataclass
class Address:
    street: str
    house_number: str
    city: str
    state: str
    zip_code: str
    country: str
