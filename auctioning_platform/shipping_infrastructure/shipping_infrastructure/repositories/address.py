from shipping import AddressRepository
from shipping.domain.entities import Address
from shipping.domain.types import ConsigneeId


class FakeAddressRepository(AddressRepository):
    def get(self, consignee_id: ConsigneeId) -> Address:
        return Address()
