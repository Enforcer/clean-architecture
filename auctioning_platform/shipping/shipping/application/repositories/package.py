import abc
import uuid

from shipping.domain.entities import Package


class PackageRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, package_uuid: uuid.UUID) -> Package:
        pass

    @abc.abstractmethod
    def save(self, package: Package) -> None:
        pass
