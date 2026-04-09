import functools
import inspect
import os
import random
import time
from collections.abc import Callable
from typing import Any, TypeVar, cast

F = TypeVar("F", bound=Callable[..., Any])
T = TypeVar("T")


def randomly_slow(env_var: str) -> Callable[[F], F]:
    """Decorator factory: wraps a sync callable to add random latency read from env_var.

    When env_var > 0, sleeps for a random step between delay_ms/10 and delay_ms
    (10 discrete steps) before calling the wrapped function.
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay_ms = int(os.environ.get(env_var, "0"))
            if delay_ms > 0:
                steps = [(i + 1) * delay_ms // 10 for i in range(10)]
                time.sleep(random.choice(steps) / 1000)
            return func(*args, **kwargs)

        return cast(F, wrapper)

    return decorator  # type: ignore[return-value]


def randomly_slow_class(env_var: str) -> Callable[[type[T]], type[T]]:
    """Class decorator factory: applies randomly_slow to all public instance methods."""

    def decorator(cls: type[T]) -> type[T]:
        for name, method in vars(cls).items():
            if not name.startswith("_") and inspect.isfunction(method):
                setattr(cls, name, randomly_slow(env_var)(method))
        return cls

    return decorator
