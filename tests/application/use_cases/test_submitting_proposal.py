from uuid import uuid4
from unittest.mock import Mock

import inject
import pytest

from application.dto import ValidationError
from application.interfaces import (
    NotificationsSender,
    ProposalsRepository,
)
from application.use_cases import SubmittingProposalUseCase
from application.notifications import NewProposalNotification


@pytest.fixture(autouse=True)
def configure_inject(proposals_repo_mock, notifications_sender_mock):

    def configure_di(binder: inject.Binder):
        binder.bind(ProposalsRepository, proposals_repo_mock)
        binder.bind(NotificationsSender, notifications_sender_mock)

    inject.clear_and_configure(configure_di)


@pytest.fixture()
def submitting_proposal_dto() -> SubmittingProposalUseCase.DTO:
    return SubmittingProposalUseCase.DTO(
        uuid=uuid4(),
        title='Clean Architecture',
        description='Exemplary description',
        author_email='john.doe@pythonlodz.org'
    )


@pytest.mark.parametrize("title, description, email", [
    ('Clean Architecture', 'Exemplary description', 'asdas'),
    ('', 'Exemplary description', 'john.doe@pythonlodz.org'),
    ('Clean Architecture', '', 'john.doe@pythonlodz.org'),
])
def test_should_raise_value_error(title, description, email):
    with pytest.raises(ValidationError):
        SubmittingProposalUseCase.DTO(uuid4(), title, description, email)


def test_should_save_proposal(submitting_proposal_dto: SubmittingProposalUseCase.DTO, proposals_repo_mock: Mock):
    use_case = SubmittingProposalUseCase()

    use_case(submitting_proposal_dto)

    save_method_mock: Mock = proposals_repo_mock.save
    assert save_method_mock.called


def test_should_send_notification_to_author(
        submitting_proposal_dto: SubmittingProposalUseCase.DTO,
        notifications_sender_mock: Mock
):
    use_case = SubmittingProposalUseCase()

    use_case(submitting_proposal_dto)

    expected_notification = NewProposalNotification(
        submitting_proposal_dto.title,
        submitting_proposal_dto.author_email
    )
    send_method_mock: Mock = notifications_sender_mock.send
    send_method_mock.assert_called_once_with(expected_notification)
