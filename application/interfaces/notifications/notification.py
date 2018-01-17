from abc import (
    ABCMeta,
    abstractmethod,
)


class Notification(metaclass=ABCMeta):

    @property
    @abstractmethod
    def title(self) -> str:
        pass

    @property
    @abstractmethod
    def contents(self) -> str:
        pass

    @property
    @abstractmethod
    def recipient(self):
        pass
