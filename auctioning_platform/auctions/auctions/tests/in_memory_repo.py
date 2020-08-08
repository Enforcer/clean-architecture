from typing import Dict

from foundation.events import EventBus

from auctions.application.repositories import AuctionsRepository
from auctions.domain.entities import Auction
from auctions.domain.value_objects import AuctionId


class InMemoryAuctionsRepo(AuctionsRepository):
    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus
        self._data: Dict[AuctionId, Auction] = {}

    def get(self, auction_id: AuctionId) -> Auction:
        return self._data[auction_id]

    def save(self, auction: Auction) -> None:
        for event in auction.domain_events:
            self._event_bus.post(event)
        auction.clear_events()
        self._data[auction.id] = auction
