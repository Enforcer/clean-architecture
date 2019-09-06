from dataclasses import dataclass
from uuid import UUID

# from shipping.application.repositories import PackagesRepository


@dataclass
class SendingPackageInputDto:
    package_uuid: UUID


class SendingPackage:
    pass
