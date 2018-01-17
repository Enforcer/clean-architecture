from abc import (
    ABCMeta,
    abstractmethod,
)
from uuid import UUID

from domain.entities import Proposal


class ProposalsRepository(metaclass=ABCMeta):

    @abstractmethod
    def get(self, uuid: UUID) -> Proposal:
        pass

    @abstractmethod
    def save(self, proposal: Proposal):
        pass
