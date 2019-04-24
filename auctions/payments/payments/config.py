from dataclasses import dataclass


@dataclass(repr=False)
class PaymentsConfig:
    login: str
    password: str
