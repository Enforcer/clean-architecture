from django.apps import AppConfig

import inject

from auctions.application.ports import EmailGateway
from auctions.application.repositories import AuctionsRepository
from auctions_infrastructure.adapters import DummyEmailGateway
from auctions_infrastructure.repositories import DjangoORMAuctionsRepository


def inject_config(binder: inject.Binder) -> None:
    binder.bind(EmailGateway, DummyEmailGateway())
    binder.bind(AuctionsRepository, DjangoORMAuctionsRepository())


class WebConfig(AppConfig):
    name = 'web'

    def ready(self) -> None:
        super().ready()
        inject.configure(inject_config)
