from typing import Callable

from pybuses import EventBus

from auctions.domain.events import BidderHasBeenOverbid, WinningBidPlaced
from customer_relationship import emails
from customer_relationship.email_sender import EmailSender
from customer_relationship.config import CustomerRelationshipConfig


class CustomerRelationshipFacade:
    def __init__(self, config: CustomerRelationshipConfig, event_bus: EventBus, enqueue_fun: Callable) -> None:
        self._sender = EmailSender(config)
        self._enqueue_fun = enqueue_fun

        event_bus.subscribe(self.send_email_about_overbid)
        event_bus.subscribe(self.send_email_about_winning)

    def send_email_about_overbid(self, event: BidderHasBeenOverbid) -> None:
        email = emails.Overbid(auction_title=event.auction_title, new_price=event.new_price)
        # TODO: create query OR sync data between contexts in different way
        self._send("sebastian@cleanarchitecture.io", email)

    def send_email_about_winning(self, event: WinningBidPlaced) -> None:
        email = emails.Winning(auction_title=event.auction_title, amount=event.bid_amount)
        # TODO: create query OR sync data between contexts in different way
        self._send("sebastian@cleanarchitecture.io", email)

    def _send(self, recipient: str, email: emails.Email) -> None:
        self._enqueue_fun(self._sender.send, recipient, email)
