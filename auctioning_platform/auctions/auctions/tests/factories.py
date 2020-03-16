import factory

from foundation.value_objects.factories import get_dollars

from auctions.domain.entities import Auction


class AuctionFactory(factory.Factory):
    class Meta:
        model = Auction

    id = factory.Sequence(lambda n: n)
    bids = factory.List([])
    title = factory.Faker("name")
    starting_price = get_dollars("10.00")
    ends_at = factory.Faker("future_datetime", end_date="+7d")
    ended = False
