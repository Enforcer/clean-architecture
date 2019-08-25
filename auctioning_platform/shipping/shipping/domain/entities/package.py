import uuid
from dataclasses import dataclass, field

from shipping.domain.types import ConsigneeId
from shipping.domain.value_objects import PackageStatus


@dataclass
class Package:
    uuid: uuid.UUID
    item_identifier: str
    consignee_id: ConsigneeId
    street: str
    house_number: str
    city: str
    state: str
    zip_code: str
    country: str
    status: PackageStatus = field(default=PackageStatus.CREATED)
