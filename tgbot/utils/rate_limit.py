from __future__ import annotations

import typing as ty

if ty.TYPE_CHECKING:
    T = ty.TypeVar("T")


def rate_limit(limit: int, key: str | None = None) -> ty.Callable[[T], T]:
    """
    Декоратор для настройки лимита использования команды.
    :param limit: 1 раз в сколько секунд можно использовать команду.
    :param key:
    :return: Декоратор.
    """

    def _decorator(func: T) -> T:
        setattr(func, "throttling_rate_limit", limit)
        if key:
            setattr(func, "throttling_key", key)
        return func

    return _decorator
