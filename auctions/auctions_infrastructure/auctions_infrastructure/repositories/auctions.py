import copy
from typing import (
    Dict,
    List,
)

import inject
import pytz
from sqlalchemy.engine import (
    Connection,
    RowProxy,
)

from auctions.application.repositories import AuctionsRepository
from auctions.domain.entities import (
    Auction,
    Bid,
)
from auctions.domain.types import AuctionId
from auctions.domain.factories import get_dollars
from auctions_infrastructure import auctions, bids


class InMemoryAuctionsRepository(AuctionsRepository):
    def __init__(self, objects: List[Auction] = None) -> None:
        if not objects:
            objects = []

        self._storage: Dict[AuctionId, Auction] = {}
        for object in objects:
            self.save(object)

    def get(self, auction_id: AuctionId) -> Auction:
        copied = copy.deepcopy(self._storage[auction_id])
        return Auction(
            id=copied.id,
            title=copied.title,
            starting_price=copied.starting_price,
            bids=copied.bids,
            ends_at=copied.ends_at,
        )

    def save(self, auction: Auction) -> None:
        copied = copy.deepcopy(auction)
        copied.bids = [bid for bid in copied.bids if bid.id not in copied.withdrawn_bids_ids]
        self._storage[auction.id] = copied


class SqlAlchemyAuctionsRepo(AuctionsRepository):

    @inject.autoparams('connection')
    def __init__(self, connection: Connection = None) -> None:
        self._conn = connection

    def get(self, auction_id: AuctionId) -> Auction:
        row = self._conn.execute(auctions.select().where(auctions.c.id == auction_id)).first()
        if not row:
            raise Exception('Not found')

        bid_rows = self._conn.execute(bids.select().where(bids.c.auction_id == auction_id)).fetchall()
        return self._row_to_entity(row, bid_rows)

    def _row_to_entity(self, auction_proxy: RowProxy, bids_proxies: List[RowProxy]) -> Auction:
        auction_bids = [Bid(bid.id, bid.bidder_id, get_dollars(bid.amount)) for bid in bids_proxies]
        return Auction(
            auction_proxy.id,
            auction_proxy.title,
            get_dollars(auction_proxy.starting_price),
            auction_bids,
            auction_proxy.ends_at.replace(tzinfo=pytz.UTC),
        )

    def save(self, auction: Auction) -> None:
        raw_auction = {
            'title': auction.title,
            'starting_price': auction.starting_price.amount,
            'current_price': auction.current_price.amount,
            'ends_at': auction.ends_at,
        }
        update_result = self._conn.execute(
            auctions.update(
                values=raw_auction,
                whereclause=auctions.c.id == auction.id
            )
        )
        assert update_result.rowcount == 1  # no support for creating

        for bid in auction.bids:
            if bid.id:
                continue
            result = self._conn.execute(bids.insert(values={
                'auction_id': auction.id, 'amount': bid.amount.amount, 'bidder_id': bid.bidder_id
            }))
            bid.id, = result.inserted_primary_key

        if auction.withdrawn_bids_ids:
            self._conn.execute(bids.delete(whereclause=bids.c.id.in_(auction.withdrawn_bids_ids)))
