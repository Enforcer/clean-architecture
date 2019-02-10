from abc import abstractmethod


class Message:
    @abstractmethod
    @property
    def title(self) -> str:
        pass

    @abstractmethod
    @property
    def html(self) -> str:
        pass

    @abstractmethod
    @property
    def text(self) -> str:
        pass


class Overbid(Message):
    def __init__(self) -> None:
        pass

    pass
