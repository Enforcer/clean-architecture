from datetime import datetime
from functools import singledispatchmethod
import json

from foundation.value_objects import Money

from auctions import AuctionDto


class JSONEncoder(json.JSONEncoder):
    @singledispatchmethod
    def default(self, obj: object) -> object:
        """
        Default implementation of the given object.

        Args:
            self: (todo): write your description
            obj: (todo): write your description
        """
        raise TypeError(f"Cannot serialize {type(obj)}")

    @default.register(AuctionDto)  # noqa: F811
    def serialize_auction_dto(self, obj: AuctionDto) -> object:
        """
        Serialize the given apction.

        Args:
            self: (todo): write your description
            obj: (todo): write your description
        """
        return {
            "id": obj.id,
            "title": obj.title,
            "current_price": obj.current_price,
            "starting_price": obj.starting_price,
            "ends_at": obj.ends_at,
        }

    @default.register(Money)  # noqa: F811
    def serialize_money(self, obj: Money) -> object:
        """
        Serialize a currency.

        Args:
            self: (todo): write your description
            obj: (todo): write your description
        """
        return {"amount": str(obj.amount), "currency": obj.currency.iso_code}

    @default.register(datetime)  # noqa: F811
    def serialize_datetime(self, obj: datetime) -> str:
        """
        Serialize datetime. datetime.

        Args:
            self: (todo): write your description
            obj: (todo): write your description
        """
        return obj.isoformat()
