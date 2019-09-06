import abc
from dataclasses import dataclass


@dataclass
class PackageDto:
    ...


class GetNextPackage(abc.ABC):
    @abc.abstractmethod
    def query(self, auction_id: int) -> PackageDto:
        pass
