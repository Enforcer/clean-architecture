from types import TracebackType
from typing import Optional, Type

from redis import StrictRedis
from typing_extensions import Literal

from foundation.locks import AlreadyLocked, Lock


class RedisLock(Lock):
    LOCK_VALUE = "LOCKED"

    def __init__(self, redis: StrictRedis, name: str, timeout: int = 30) -> None:
        self._redis = redis
        self._lock_name = name
        self._timeout = timeout

    def __enter__(self) -> None:
        if not self._redis.set(self._lock_name, self.LOCK_VALUE, nx=True, ex=self._timeout):
            raise AlreadyLocked

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> Literal[False]:
        if exc_type != AlreadyLocked:
            self._redis.delete(self._lock_name)
        return False
