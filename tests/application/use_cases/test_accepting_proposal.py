from unittest.mock import Mock

import inject
import pytest

from application.interfaces import (
    ProposalsRepository,
    NotificationsSender,
)
from application.use_cases import AcceptingProposalUseCase
from application.notifications import ProposalAcceptedNotification
from domain.entities import Proposal
from domain.enums import ProposalStatus


@pytest.fixture(autouse=True)
def configure_inject(proposals_repo_mock: Mock, example_new_proposal: Proposal, notifications_sender_mock: Mock):

    proposals_repo_mock.get.return_value = example_new_proposal

    def configure_di(binder: inject.Binder):
        binder.bind(ProposalsRepository, proposals_repo_mock)
        binder.bind(NotificationsSender, notifications_sender_mock)

    inject.clear_and_configure(configure_di)


def test_should_change_status_to_accepted(example_new_proposal: Proposal, proposals_repo_mock: Mock):
    call_use_case_for_proposal(example_new_proposal)

    assert example_new_proposal.status == ProposalStatus.ACCEPTED
    proposals_repo_mock.save.assert_called_once_with(example_new_proposal)


def test_should_write_changed_proposal(example_new_proposal: Proposal, proposals_repo_mock: Mock):
    call_use_case_for_proposal(example_new_proposal)

    proposals_repo_mock.save.assert_called_once_with(example_new_proposal)


def test_should_send_notification(example_new_proposal: Proposal, notifications_sender_mock: Mock):
    call_use_case_for_proposal(example_new_proposal)

    expected_notification = ProposalAcceptedNotification(example_new_proposal.title, example_new_proposal.author_email)
    send_mock: Mock = notifications_sender_mock.send
    send_mock.assert_called_once_with(expected_notification)


def call_use_case_for_proposal(proposal: Proposal):
    use_case = AcceptingProposalUseCase()
    dto = AcceptingProposalUseCase.DTO(proposal.uuid)

    use_case(dto)
