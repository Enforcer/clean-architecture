from types import TracebackType
from typing import Callable, Optional, Type

from typing_extensions import Literal, Protocol


class AlreadyLocked(Exception):
    pass


class Lock(Protocol):
    def __enter__(self) -> None:
        """
        Inspector.

        Args:
            self: (todo): write your description
        """
        ...

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> Literal[False]:
        """
        Exit the given exception.

        Args:
            self: (todo): write your description
            exc_type: (todo): write your description
            Type: (todo): write your description
            exc_val: (todo): write your description
            exc_tb: (todo): write your description
        """
        ...


LockFactory = Callable[[str, int], Lock]
