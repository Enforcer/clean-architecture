from dataclasses import dataclass
from typing import Tuple


@dataclass(repr=False)
class CustomerRelationshipConfig:
    email_host: str
    email_port: int
    email_username: str
    email_password: str
    email_from: Tuple[str, str]

    @property
    def formatted_from(self) -> str:
        return f"{self.email_from[0]} <{self.email_from[1]}>"
