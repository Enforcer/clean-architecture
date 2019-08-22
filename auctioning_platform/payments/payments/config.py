from dataclasses import dataclass


@dataclass(repr=False)
class PaymentsConfig:
    username: str
    password: str
