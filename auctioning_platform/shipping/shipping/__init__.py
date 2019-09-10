import injector

from shipping.application.queries import GetNextPackage, PackageDto
from shipping.application.repositories import AddressRepository

__all__ = [
    # module
    "Shipping",
    # events
    # repositories
    "AddressRepository",
    # use cases
    # queries
    "GetNextPackage",
    "PackageDto",
]


class Shipping(injector.Module):
    pass
