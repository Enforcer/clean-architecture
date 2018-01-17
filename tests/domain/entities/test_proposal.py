import pytest

from domain.entities import Proposal
from domain.enums import ProposalStatus
from domain.exceptions import CanNotChangeProposalStatus


def test_should_allow_for_setting_accepted(example_new_proposal: Proposal) -> None:
    example_new_proposal.accept()

    assert example_new_proposal.status == ProposalStatus.ACCEPTED


def test_should_allow_for_setting_rejected(example_new_proposal: Proposal) -> None:
    example_new_proposal.reject()

    assert example_new_proposal.status == ProposalStatus.REJECTED


def test_should_not_allow_for_rejecting_accepted_proposal(example_accepted_proposal: Proposal) -> None:
    with pytest.raises(CanNotChangeProposalStatus):
        example_accepted_proposal.reject()


def test_should_not_allow_for_accepting_rejected_proposal(example_rejected_proposal: Proposal) -> None:
    with pytest.raises(CanNotChangeProposalStatus):
        example_rejected_proposal.accept()
