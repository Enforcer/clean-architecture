from pybuses import EventBus

from auctions.domain.events import BidderHasBeenOverbid
from customer_relationship import messages
from customer_relationship.email_sender import EmailSender
from customer_relationship.config import CustomerRelationshipConfig


class CustomerRelationshipFacade:
    def __init__(self, config: CustomerRelationshipConfig, event_bus: EventBus) -> None:
        self._sender = EmailSender(config)

        # event_bus.subscribe(self.send_email_about_overbid)

    def send_email_about_overbid(self, event: BidderHasBeenOverbid) -> None:
        message = messages.Overbid(
            auction_title=(lambda auction_id: f"<Auction {auction_id}")(event.auction_id),  # TODO: create query
            new_price=event.new_price,
        )
        recipient = (lambda bidder_id: "sebastian@cleanarchitecture.io")(event.bidder_id)  # TODO: create query
        self._sender.send(recipient, message)
