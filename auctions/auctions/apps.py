from django.apps import AppConfig

import inject

from auctions.application.interfaces import EmailGateway
from auctions.application.repositories import AuctionsRepository
from auctions.application.use_cases import (
    placing_bid,
    withdrawing_bids,
)
from auctions.infrastructure.repositories import DjangoORMAuctionsRepository


class AuctionsConfig(AppConfig):
    name = 'auctions'

    def ready(self) -> None:
        super().ready()

        def config(binder: inject.Binder) -> None:
            binder.bind(EmailGateway, None)  # add implementation once it's done
            binder.bind(AuctionsRepository, DjangoORMAuctionsRepository())

        inject.configure(config)
