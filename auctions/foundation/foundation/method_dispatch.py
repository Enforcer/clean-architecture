import functools
from typing import Callable


def method_dispatch(func: Callable) -> Callable:
    dispatcher = functools.singledispatch(func)

    def wrapper(*args, **kw):
        return dispatcher.dispatch(args[1].__class__)(*args, **kw)

    wrapper.register = dispatcher.register  # type: ignore
    functools.update_wrapper(wrapper, func)
    return wrapper
