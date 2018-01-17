import json
from uuid import UUID

import inject

from application.configuration import Config
from application.interfaces import (
    NotFound,
    ProposalsRepository,
)
from domain.entities import Proposal
from domain.enums import ProposalStatus


class FileProposalsRepository(ProposalsRepository):
    config: Config = inject.attr(Config)

    def _get_file_contents(self) -> dict:
        with open(self.config.PROPOSALS_REPO_FILE, 'a+') as file:
            file.seek(0)
            contents = file.read()
            if not contents:
                return {}
            else:
                return json.loads(contents)

    def save(self, proposal: Proposal):
        contents = self._get_file_contents()
        contents[str(proposal.uuid)] = {
            'title': proposal.title,
            'description': proposal.description,
            'author_email': proposal.author_email,
            'status': proposal.status.value
        }

        with open(self.config.PROPOSALS_REPO_FILE, 'w') as file:
            contents = json.dumps(contents, indent=4, sort_keys=True)
            file.write(contents)

    def get(self, uuid: UUID) -> Proposal:
        contents = self._get_file_contents()

        try:
            proposal_raw = contents[str(uuid)]
        except KeyError:
            raise NotFound

        return Proposal(
            uuid=uuid,
            title=proposal_raw['title'],
            description=proposal_raw['description'],
            author_email=proposal_raw['author_email'],
            status=ProposalStatus(proposal_raw['status'])
        )
