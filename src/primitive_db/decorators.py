"""Reusable wrappers and a cache backed by a closure."""

from collections.abc import Callable, Hashable
from functools import wraps
from time import monotonic
from typing import ParamSpec, TypeVar

import prompt

P = ParamSpec("P")
R = TypeVar("R")


def handle_db_errors(func: Callable[P, R]) -> Callable[P, R | None]:
    """Report database exceptions without stopping the command loop."""
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
        """Run the wrapped operation with the added decorator behavior."""
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as error:
            print(f"Ошибка: Таблица или столбец {error} не найден.")
        except ValueError as error:
            print(f"Ошибка валидации: {error}")
        except Exception as error:
            print(f"Произошла непредвиденная ошибка: {error}")
        return None

    return wrapper


def confirm_action(
    action_name: str,
) -> Callable[[Callable[P, R]], Callable[P, R | None]]:
    """Require an explicit y before performing a destructive action."""
    def decorator(func: Callable[P, R]) -> Callable[P, R | None]:
        """Wrap an operation with a confirmation prompt."""
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
            """Run the wrapped operation with the added decorator behavior."""
            try:
                answer = prompt.string(
                    f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ',
                    empty=True,
                )
            except (EOFError, KeyboardInterrupt):
                print("\nОперация отменена.")
                return None
            if answer != "y":
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func: Callable[P, R]) -> Callable[P, R]:
    """Print execution duration while preserving the function result."""
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        """Run the wrapped operation with the added decorator behavior."""
        started = monotonic()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = monotonic() - started
            print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд")

    return wrapper


def create_cacher() -> Callable[[Hashable, Callable[[], R]], R]:
    """Create a function that stores successful results in a closure."""
    cache = {}

    def cache_result(key: Hashable, value_func: Callable[[], R]) -> R:
        """Return a cached value or compute and remember it."""
        if key not in cache:
            cache[key] = value_func()
        return cache[key]

    return cache_result
