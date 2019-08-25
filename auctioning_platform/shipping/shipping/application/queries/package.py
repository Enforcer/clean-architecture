import abc
import uuid
from dataclasses import dataclass
from typing import Optional


@dataclass
class PackageDto:
    uuid: uuid.UUID
    item_identifier: str
    street: str
    house_number: str
    city: str
    state: str
    zip_code: str
    country: str


class GetNextPackage(abc.ABC):
    @abc.abstractmethod
    def query(self) -> Optional[PackageDto]:
        pass
