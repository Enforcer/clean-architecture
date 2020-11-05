from typing import List

from sqlalchemy import func
from sqlalchemy.engine import RowProxy

from foundation.value_objects.factories import get_dollars

from auctions.application.queries import AuctionDto, GetActiveAuctions, GetSingleAuction
from auctions_infrastructure import auctions
from auctions_infrastructure.queries.base import SqlQuery


class SqlGetActiveAuctions(GetActiveAuctions, SqlQuery):
    def query(self) -> List[AuctionDto]:
        """
        Returns a list of query.

        Args:
            self: (todo): write your description
        """
        return [
            _row_to_dto(row) for row in self._conn.execute(auctions.select().where(auctions.c.ends_at > func.now()))
        ]


class SqlGetSingleAuction(GetSingleAuction, SqlQuery):
    def query(self, auction_id: int) -> AuctionDto:
        """
        Query the database.

        Args:
            self: (todo): write your description
            auction_id: (str): write your description
        """
        row = self._conn.execute(auctions.select().where(auctions.c.id == auction_id)).first()
        return _row_to_dto(row)


def _row_to_dto(auction_proxy: RowProxy) -> AuctionDto:
    """
    This method touction object for a proxy.

    Args:
        auction_proxy: (todo): write your description
    """
    return AuctionDto(
        id=auction_proxy.id,
        title=auction_proxy.title,
        current_price=get_dollars(auction_proxy.current_price),
        starting_price=get_dollars(auction_proxy.starting_price),
        ends_at=auction_proxy.ends_at,
    )
