from types import TracebackType
from typing import Callable, Optional, Type

from typing_extensions import Protocol


class AlreadyLocked(Exception):
    pass


class Lock(Protocol):
    def __enter__(self) -> None:
        ...

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> bool:
        ...


LockFactory = Callable[[str, int], Lock]
