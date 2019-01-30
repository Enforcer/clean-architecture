from dataclasses import dataclass
from pybuses import EventBus

from auctions.domain.events import BidderHasBeenOverbid


@dataclass(repr=False)
class CustomerRelationshipConfig:
    email_host: str
    email_port: int
    email_username: str
    email_password: str


class CustomerRelationshipFacade:
    def __init__(self, config: CustomerRelationshipConfig, event_bus: EventBus) -> None:
        self._config = config

        event_bus.subscribe(self.send_email_about_overbid)

    def send_email_about_overbid(self, event: BidderHasBeenOverbid) -> None:
        print("dummy handler", event, self._config)
