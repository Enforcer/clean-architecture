import functools
from typing import Any, Callable


def method_dispatch(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to dispatch a function.

    Args:
        func: (todo): write your description
        Callable: (todo): write your description
        Any: (todo): write your description
    """
    dispatcher = functools.singledispatch(func)

    def wrapper(*args, **kw):  # type: ignore
        """
        Decorator to dispatch a method.

        Args:
            kw: (todo): write your description
        """
        return dispatcher.dispatch(args[1].__class__)(*args, **kw)

    wrapper.register = dispatcher.register  # type: ignore
    wrapper.registry = dispatcher.registry  # type: ignore
    functools.update_wrapper(wrapper, func)
    return wrapper
