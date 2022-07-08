from __future__ import annotations

import re
import typing as ty
from functools import wraps
from inspect import signature, iscoroutinefunction

from aiogram.types import Message
from aiogram.utils.markdown import hbold, hcode
from loguru import logger

from utils.exceptions import (
    InvalidArgumentsError,
    ParamsError,
    RequiredArgumentNotPassed,
    TimedeltaParseError,
)
from utils.safe_list import SafeList
from .resolve_type import resolve_type

if ty.TYPE_CHECKING:
    from utils.handler_params.base import HandlerParam

    T = ty.TypeVar("T")


def command_handler(
    func: ty.Callable[..., ty.Awaitable[T]]
) -> ty.Callable[[Message], ty.Awaitable[T]]:
    """
    Декоратор для обработчиков команд.
    Реализует подготовку параметров обработчика.
    :param func: Обработчик.
    :return: Обертка.
    """
    if not iscoroutinefunction(func):
        raise TypeError(f"Function `{func.__name__}` must be coroutine function")

    setup_handler_params(func)

    @wraps(func)
    async def _wrapper(message: Message) -> T:
        params = await make_handler_params(func, message)
        return await func(**params)

    return _wrapper


def set_usage_pattern(usage_pattern: str) -> ty.Callable[[T], T]:
    """
    Декоратор, устанавливающий шаблон использования команды.
    Этот шаблон показывается пользователю, если он некорректно использует команду.
    :param usage_pattern: Шаблон использования команды.
    """

    def _decorator(func: T) -> T:
        func.__dict__["usage_pattern"] = hcode(usage_pattern)
        return func

    return _decorator


def setup_handler_params(func: ty.Callable[..., ty.Awaitable[T]]) -> None:
    """
    Подготовка обработчика команды.
    Создание списка параметров.
    :param func: Обработчик команды.
    """
    params = func.__dict__["params"] = list()  # Список параметров
    # Анализируем какие параметры принимает обработчик
    for name, argument in signature(func).parameters.items():
        params.append(resolve_type(argument))  # Создаем параметр

    logger.opt(colors=True).trace(
        f"Handler <e>{func.__name__}</e> params setup finished: "
        f"[{', '.join(f'{param:colored}' for param in params)}]",
    )


async def make_handler_params(
    func: ty.Callable[..., ty.Awaitable[T]], message: Message
) -> dict[str, ty.Any]:
    """
    Сбор параметров для обработчика.
    :param func: Обработчик команды.
    :param message: Сообщение.
    :return: Параметры, которые нужно передать в обработчик.
    """
    handler_params: list[HandlerParam] = func.__dict__["params"]
    params: dict[str, ty.Any] = {}
    args = SafeList(message.get_args().split())  # Текстовые аргументы от пользователя

    for param in handler_params:
        try:
            # Вызываем катер
            parsing_response = await param.cutter.get(message, args)
        except RequiredArgumentNotPassed:
            raise InvalidArgumentsError(
                "Не передано значение для обязательного параметра "
                f"{hbold(param.param_settings.name)}.{param.param_settings.description}"
                if param.param_settings.name
                else None
                # Если не указано название параметра, то не показываем это объяснение
            )
        except (ParamsError, TimedeltaParseError) as e:
            raise InvalidArgumentsError(
                "Некорректное значение для параметра "
                f"{hbold(param.param_settings.name)}.{param.param_settings.description} "
                f"{e.text if e.text else ''}"
                if param.param_settings.name
                else None
                # Если не указано название параметра, то не показываем это объяснение
            )
        else:
            args = parsing_response.new_args
            params[param.param_name] = parsing_response.value

    logger.opt(colors=True).trace(
        "Making params for handler <e>{handler_name}</e> finished: {{{params}}}".format(
            handler_name=func.__name__,
            params=", ".join(
                f"<lr>{key}</lr>=<ly>{_safe_text(str(value))}</ly>"
                for key, value in params.items()
            ),
        )
    )

    # Если остались лишние аргументы
    if len(args) > 0:
        raise InvalidArgumentsError

    return params


def _safe_text(text: str) -> str:
    """
    Делаем текст безопасным для вывода с помощью loguru.
    Экранируем теги. '<aboba>' -> r'\<aboba>'
    """
    if isinstance(text, str):
        return re.sub(r"<(?P<obj>\S*)>", r"\<\g<obj>>", text)
    return text
