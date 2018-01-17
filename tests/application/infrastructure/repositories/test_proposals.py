from uuid import uuid4

import inject
import pytest

from application.configuration import Config
from application.interfaces import NotFound
from domain.entities import Proposal
from infrastructure.repositories import FileProposalsRepository


@pytest.fixture(autouse=True)
def configure_inject(example_configuration: Config):

    def config(binder: inject.Binder):
        binder.bind(Config, example_configuration)

    inject.clear_and_configure(config)


def test_should_raise_not_found():
    repo = FileProposalsRepository()

    with pytest.raises(NotFound):
        repo.get(uuid4())


def test_should_save_proposal(example_new_proposal: Proposal):
    repo = FileProposalsRepository()

    repo.save(example_new_proposal)
    proposal = repo.get(example_new_proposal.uuid)

    assert_proposals_identical(example_new_proposal, proposal)


def assert_proposals_identical(one: Proposal, another: Proposal):
    assert one.uuid == another.uuid
    assert one.title == another.title
    assert one.description == another.description
    assert one.author_email == another.author_email
    assert one.status == another.status
