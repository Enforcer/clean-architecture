import abc

from shipping.domain.entities import Package


class PackageRepository(abc.ABC):
    @abc.abstractmethod
    def save(self, package: Package) -> None:
        pass
