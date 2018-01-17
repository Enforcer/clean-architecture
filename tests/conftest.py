import os
from uuid import uuid4
from unittest.mock import Mock

import pytest

from application.configuration import Config
from application.interfaces import (
    NotificationsSender,
    ProposalsRepository,
)
from domain.entities import Proposal
from domain.enums import ProposalStatus


@pytest.fixture()
def example_author_email() -> str:
    return 'john.doe@pythonlodz.org'


@pytest.fixture()
def example_new_proposal(example_author_email: str) -> Proposal:
    return example_proposal(ProposalStatus.NEW, example_author_email)


@pytest.fixture()
def example_accepted_proposal(example_author_email: str) -> Proposal:
    return example_proposal(ProposalStatus.ACCEPTED, example_author_email)


@pytest.fixture()
def example_rejected_proposal() -> Proposal:
    return example_proposal(ProposalStatus.REJECTED, example_author_email)


def example_proposal(status: ProposalStatus, author_email: str):
    return Proposal(
        uuid=uuid4(),
        title='Clean architecture',
        description='Will see',
        author_email=author_email,
        status=status
    )


@pytest.fixture()
def example_configuration(tmpdir: str) -> Config:
    return Config(
        'contact@pythonlodz.org',
        'contact@pythonlodz.org',
        os.path.join(tmpdir, 'proposals.json'),
        'postmark-token-irrelevant'
    )


@pytest.fixture()
def proposals_repo_mock() -> Mock:
    return Mock(spec_set=ProposalsRepository)


@pytest.fixture()
def notifications_sender_mock() -> Mock:
    return Mock(spec_set=NotificationsSender)
