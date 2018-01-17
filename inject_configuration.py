import inject

from application.configuration import Config
from application.interfaces import (
    NotificationsSender,
    ProposalsRepository,
)

from infrastructure.notifications import PostmarkEmailSender
from infrastructure.repositories import FileProposalsRepository


def configure(config: Config):

    def configure_inject(binder: inject.Binder):
        binder.bind(NotificationsSender, PostmarkEmailSender())
        binder.bind(ProposalsRepository, FileProposalsRepository())
        binder.bind(Config, config)

    inject.configure_once(configure_inject)
