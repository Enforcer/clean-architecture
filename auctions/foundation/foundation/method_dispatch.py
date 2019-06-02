import functools
from typing import Any, Callable


def method_dispatch(func: Callable[..., Any]) -> Callable[..., Any]:
    dispatcher = functools.singledispatch(func)

    def wrapper(*args, **kw):  # type: ignore
        return dispatcher.dispatch(args[1].__class__)(*args, **kw)

    wrapper.register = dispatcher.register  # type: ignore
    wrapper.registry = dispatcher.registry  # type: ignore
    functools.update_wrapper(wrapper, func)
    return wrapper
