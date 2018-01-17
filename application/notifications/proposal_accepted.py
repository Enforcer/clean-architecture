import attr
import inject

from application.configuration import Config
from application.interfaces import Notification


@attr.s
class ProposalAcceptedNotification(Notification):
    proposal_title: str = attr.ib()
    author_email: str = attr.ib()

    config: Config = inject.attr(Config)

    @property
    def title(self) -> str:
        return f'Zgłoszenie talka "{self.proposal_title}" zaakceptowane!'

    @property
    def contents(self) -> str:
        return f'''Cześć,

bardzo miło nam poinformować, że Twój talk zatytułowany "{self.proposal_title}" został zaakceptowany!

Już niedługo dostaniesz dalsze informacje.
        '''

    @property
    def recipient(self) -> str:
        return self.author_email
