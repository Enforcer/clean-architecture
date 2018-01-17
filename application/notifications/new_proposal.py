import attr
import inject

from application.configuration import Config
from application.interfaces import Notification


@attr.s
class NewProposalNotification(Notification):
    proposal_title: str = attr.ib()
    author_email: str = attr.ib()

    config: Config = inject.attr(Config)

    @property
    def title(self) -> str:
        return f'Nowe zgłoszenie talka - "{self.proposal_title}"'

    @property
    def contents(self) -> str:
        return f'{self.author_email} właśnie zaproponował/a talka zatytułowanego "{self.proposal_title}"'

    @property
    def recipient(self) -> str:
        return self.config.PROPOSALS_NOTIFICATIONS_RECIPIENT
