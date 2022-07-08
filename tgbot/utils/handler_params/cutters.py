from __future__ import annotations

import typing as ty

from services.find_target_user import get_target_user, get_db_user_by_tg_user
from utils.exceptions import ParamsError, RequiredArgumentNotPassed
from utils.timedelta_functions import timedelta, parse_timedelta_from_text
from .base import (
    Cutter,
    CtxDataCutter,
    TextArgumentCutter,
    BaseTypeCutter,
    CutterParsingResponse,
)

T = ty.TypeVar("T")

if ty.TYPE_CHECKING:
    from aiogram.types import Message
    from utils.safe_list import SafeList


class MessageCutter(Cutter):
    """
    Катер сообщения.
    Ussage:
        >>> from aiogram.types import Message
        >>> from utils.handler_params import command_handler
        >>> @command_handler
        ... async def handler(message: Message): ...
    """

    async def _get(self, message: Message, args: SafeList) -> CutterParsingResponse:
        return CutterParsingResponse(message, args)


class ChatCutter(CtxDataCutter):
    """
    Катер чата из контекста команды.
    Ussage:
        >>> from models.db import Chat
        >>> from utils.handler_params import command_handler
        >>> @command_handler
        ... async def handler(chat: Chat): ...
    """

    @property
    def var_name(self) -> str:
        return "chat"


class SenderCutter(CtxDataCutter):
    """
    Катер отправителя из контекста команды.
    Ussage:
        >>> from models.db import User
        >>> from utils.handler_params import command_handler
        >>> @command_handler
        ... async def handler(sender: User): ...
    """

    @property
    def var_name(self) -> str:
        return "user"


class IntegerCutter(BaseTypeCutter):
    """
    Целочисленный числовой аргумент.
    Ussage:
        >>> from utils.handler_params import command_handler
        >>> @command_handler
        ... async def handler(num: int): ...
    """

    factory = int


class FloatCutter(BaseTypeCutter):
    """
    Аргумент числа с плавающей точкой.
    Ussage:
        >>> from utils.handler_params import command_handler
        >>> @command_handler
        ... async def handler(num: float): ...
    """

    factory = float


class WordCutter(BaseTypeCutter):
    """
    Текстовый аргумент.
    Одно слово.
    Ussage:
        >>> from utils.handler_params import command_handler
        >>> @command_handler
        ... async def handler(word: str): ...
    """

    factory = str


class StringCutter(TextArgumentCutter):
    """
    Текстовый аргумент.
    Забирает все оставшиеся аргументы команды.
    Ussage:
        >>> from utils.handler_params import command_handler
        >>> @command_handler
        ... async def handler(*, string: str):
        ...     # Название параметра не играет значения,
        ...     # StringCutter достигается обозначением KEYWORD_ONLY
    """

    async def _get(self, message: Message, args: SafeList) -> CutterParsingResponse:
        return CutterParsingResponse(" ".join(args), args.cleared())


class OptionalCutter(Cutter):
    """
    Не обязательный аргумент.
    Ussage:
        >>> import typing
        >>> from utils.handler_params import command_handler
        >>> @command_handler
        ... async def handler(param: typing.Optional[str]): ...
        или
        >>> @command_handler
        ... async def handler(param: str | None): ...
        ...     # None в этом случае должен быть на втором месте
    """

    def __init__(
        self,
        arg_type: Cutter,
        /,
        *,
        default: ty.Any | None = None,
        default_factory: ty.Callable[[], ty.Any] | None = None,
    ) -> None:
        self._default = default
        self._default_factory = default_factory
        self._arg_type = arg_type

    async def _get(self, message: Message, args: SafeList) -> CutterParsingResponse:
        try:
            return await self._arg_type.get(message, args)
        except RequiredArgumentNotPassed:
            if self._default_factory is not None:
                return CutterParsingResponse(self._default_factory(), args)
            else:
                # `None` или установленное значение
                return CutterParsingResponse(self._default, args)

    def __repr__(self):
        return f"<{self.__class__.__name__} ({self._arg_type!r})>"

    def __format__(self, format_spec):
        if format_spec == "colored":
            return (
                f"<lc><{self.__class__.__name__}</lc> "
                f"({self._arg_type:colored})<lc>></lc>"
            )
        return repr(self)


class UnionCutter(TextArgumentCutter):
    """
    Аргумент с несколькими допустимыми типами.
    Ussage:
        >>> import typing
        >>> from utils.handler_params import command_handler
        >>> @command_handler
        ... async def handler(param: typing.Union[int, float]): ...
        или
        >>> @command_handler
        ... async def handler(param: int | float): ...
    """

    def __init__(self, *arg_types: Cutter):
        self._arg_types = arg_types

    async def _get(self, message: Message, args: SafeList) -> CutterParsingResponse:
        for arg_type in self._arg_types:
            try:
                parsed_value = await arg_type.get(message, args)
            except ParamsError:
                continue
            else:
                return parsed_value

        raise ParamsError

    def __repr__(self):
        return f"<{self.__class__.__name__} ({' | '.join(map(repr, self._arg_types))})>"

    def __format__(self, format_spec):
        if format_spec == "colored":
            return (
                f"<lc><{self.__class__.__name__}</lc> "
                f"({' | '.join(map(str, f'{self._arg_types:colored}'))})<lc>></lc>"
            )
        return repr(self)


class LiteralCutter(TextArgumentCutter):
    """
    Аргумент с определенным значением.
    Ussage:
        >>> import typing
        >>> from utils.handler_params import command_handler
        >>> @command_handler
        ... async def handler(param: typing.Literal["one", "two"]): ...
    """

    def __init__(self, *container_values: str):
        self._container_values = container_values

    async def _get(self, message: Message, args: SafeList) -> CutterParsingResponse:
        for value in self._container_values:
            if args[0] == value:
                return CutterParsingResponse(value, args[1:])

        raise ParamsError

    def __repr__(self):
        return f"<{self.__class__.__name__} ({' | '.join(self._container_values)})>"

    def __format__(self, format_spec):
        if format_spec == "colored":
            return (
                f"<lc><{self.__class__.__name__}</lc> "
                f"({' | '.join(map(repr, f'{self._container_values:colored}'))})<lc>></lc>"
            )
        return repr(self)


class Timedelta(TextArgumentCutter, timedelta):
    """
    Аргумент с временным отрезком.
    Ussage:
        >>> from utils.handler_params import command_handler
        >>> from utils.handler_params.cutters import Timedelta
        >>> @command_handler
        ... async def handler(duration: Timedelta): ...
    """

    async def _get(self, message: Message, args: SafeList) -> CutterParsingResponse:
        duration, match = parse_timedelta_from_text(
            line if (line := " ".join(args)) else None
        )
        return CutterParsingResponse(duration, args[len(match.string.split()) :])


class TargetCutter(Cutter):
    """
    Аргумент с временным отрезком.
    Ussage:
        >>> from utils.handler_params import command_handler
        >>> from utils.handler_params.cutters import TargetCutter
        >>> @command_handler
        ... async def handler(param: TargetCutter): ...
        ...     # В данном случае название аргумента не играет значения
        или
        >>> from models.db import User
        >>> @command_handler
        ... async def handler(target: User): ...
        ...     # В данном случае название аргумента играет значения
        или
        >>> @command_handler
        ... async def handler(target_user: User): ...
        ...     # В данном случае название аргумента играет значения
        ...     # В отличие от предыдущего случая, здесь боты не будут обработаны
    """

    def __init__(self, can_be_bot: bool = True):
        self.can_be_bot = can_be_bot

    async def _get(self, message: Message, args: SafeList) -> CutterParsingResponse:
        getting_response = get_target_user(message, args, self.can_be_bot)
        if getting_response is None:
            raise RequiredArgumentNotPassed
        target_user, new_args = getting_response
        try:
            target_user = await get_db_user_by_tg_user(target_user)
        except RuntimeError:
            raise ParamsError("\nНе удалось получить данные о пользователе")

        return CutterParsingResponse(
            await target_user, args if new_args is None else new_args
        )


__all__ = [
    "Cutter",
    "MessageCutter",
    "ChatCutter",
    "SenderCutter",
    "TargetCutter",
    "IntegerCutter",
    "FloatCutter",
    "WordCutter",
    "StringCutter",
    "OptionalCutter",
    "UnionCutter",
    "LiteralCutter",
    "Timedelta",
]
