import injector

from shipping.application.repositories import AddressRepository

__all__ = [
    # module
    "Shipping",
    # events
    # repositories
    "AddressRepository",
    # use cases
    # queries
]


class Shipping(injector.Module):
    pass
