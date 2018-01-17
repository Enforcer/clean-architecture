from uuid import UUID

from ..enums.proposal_status import ProposalStatus
from ..exceptions import CanNotChangeProposalStatus


class Proposal:

    def __init__(self, uuid: UUID, title: str, description: str, author_email: str, status: ProposalStatus) -> None:
        self.uuid = uuid
        self.title = title
        self.description = description
        self.author_email = author_email
        self.status = status

    def accept(self) -> None:
        if self.status == ProposalStatus.REJECTED:
            raise CanNotChangeProposalStatus

        self.status = ProposalStatus.ACCEPTED

    def reject(self) -> None:
        if self.status == ProposalStatus.ACCEPTED:
            raise CanNotChangeProposalStatus

        self.status = ProposalStatus.REJECTED
