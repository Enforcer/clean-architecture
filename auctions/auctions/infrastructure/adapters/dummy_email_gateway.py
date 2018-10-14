from auctions.application.ports import EmailGateway


class DummyEmailGateway(EmailGateway):

    def notify_about_winning_auction(self, auction_id: int, winner_id: int) -> None:
        pass
