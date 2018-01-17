from uuid import UUID

import inject

from application.interfaces import (
    NotificationsSender,
    ProposalsRepository,
)
from application.notifications import ProposalAcceptedNotification
from application.dto import (
    BaseDTO,
    attrib,
)


class AcceptingProposalUseCase:

    class DTO(BaseDTO):
        proposal_uuid: UUID = attrib()

    proposals_repo: ProposalsRepository = inject.attr(ProposalsRepository)
    notifications_sender: NotificationsSender = inject.attr(NotificationsSender)

    def __call__(self, dto: DTO) -> None:
        proposal = self.proposals_repo.get(dto.proposal_uuid)
        proposal.accept()
        self.proposals_repo.save(proposal)

        notification = ProposalAcceptedNotification(proposal.title, proposal.author_email)
        self.notifications_sender.send(notification)
