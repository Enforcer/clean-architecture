import uuid

import faker

from shipping import AddressRepository
from shipping.domain.entities import Address
from shipping.domain.value_objects import ConsigneeId


class FakeAddressRepository(AddressRepository):
    def get(self, consignee_id: ConsigneeId) -> Address:
        fake = faker.Faker()
        return Address(
            uuid=uuid.uuid4(),
            street=fake.street_name(),
            house_number=fake.building_number(),
            city=fake.city(),
            state=fake.state(),
            zip_code=fake.zipcode(),
            country=fake.country(),
        )
