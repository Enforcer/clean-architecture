import abc
from dataclasses import dataclass
from typing import Optional


@dataclass
class PackageDto:
    ...


class GetNextPackage(abc.ABC):
    @abc.abstractmethod
    def query(self) -> Optional[PackageDto]:
        pass
