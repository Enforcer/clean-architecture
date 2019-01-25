from auctions.domain.events import BidderHasBeenOverbid


def send_email_about_overbid(_event: BidderHasBeenOverbid) -> None:
    pass
