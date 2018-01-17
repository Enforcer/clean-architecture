from uuid import UUID

import inject
import validator

from application.dto import (
    BaseDTO,
    attrib,
    validators,
)
from application.interfaces import (
    NotificationsSender,
    ProposalsRepository,
)
from application.notifications import NewProposalNotification
from domain.entities import Proposal
from domain.enums import ProposalStatus


class SubmittingProposalUseCase:

    class DTO(BaseDTO):
        uuid: UUID = attrib()
        title: str = attrib([validator.Length(3, 255)])
        description: str = attrib([validator.Length(3, 255)])
        author_email: str = attrib([validator.Length(3, 255), validators.EmailValidator()])

    proposals_repo: ProposalsRepository = inject.attr(ProposalsRepository)
    notifications_sender: NotificationsSender = inject.attr(NotificationsSender)

    def __call__(self, dto: DTO) -> None:
        proposal = self._create_proposal(dto)
        self.proposals_repo.save(proposal)

        notification = NewProposalNotification(dto.title, dto.author_email)
        self.notifications_sender.send(notification)

    def _create_proposal(self, dto: DTO) -> Proposal:
        return Proposal(
            uuid=dto.uuid,
            title=dto.title,
            description=dto.description,
            author_email=dto.author_email,
            status=ProposalStatus.NEW
        )
