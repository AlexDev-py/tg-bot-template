from __future__ import annotations

import typing as ty
from abc import ABC, abstractmethod
from dataclasses import dataclass

from aiogram.dispatcher.handler import ctx_data

from utils.exceptions import (
    ParamsError,
    RequiredArgumentNotPassed,
)

T = ty.TypeVar("T")

if ty.TYPE_CHECKING:
    from aiogram.types import Message
    from utils.safe_list import SafeList


@dataclass
class CutterParsingResponse(ty.Generic[T]):
    """
    Результат работы катера.
    """

    value: T  # Полученное значение
    new_args: SafeList  # Новый список аргументов команды


class Cutter(ABC):
    """
    Базовый катер.
    Механизм сборки параметров для обработчика команды.
    """

    async def get(self, message: Message, args: SafeList) -> CutterParsingResponse:
        try:
            return await self._get(message, args)
        except ValueError:
            raise ParamsError

    @abstractmethod
    async def _get(self, message: Message, args: SafeList) -> CutterParsingResponse:
        """
        Вызов катера.
        Метод должен быть переопределен в наследуемом классе.
        :type message: Message.
        :type args: SafeList.
        :return: CutterParsingResponse.
        """

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def __format__(self, format_spec) -> str:
        """
        Вызывается при вставке экземпляра в строку методом str.format или f-строкой.
        :param format_spec: Модификатор.
            colored - Подготавливает строку к цветному выводу в консоль.
        """
        if format_spec == "colored":
            return rf"<lc>\{self!r}</lc>"
        return repr(self)


class CtxDataCutter(Cutter, ABC):
    """
    Базовый катер данных из контекста команды.
    Значение получается из контекста текущей команды.
    """

    @property
    @abstractmethod
    def var_name(self) -> str:
        """
        Название переменной в контексте
        """
        raise NotImplementedError(
            f"В катере {self} не определено название переменной контекста"
        )

    async def _get(self, message: Message, args: SafeList) -> CutterParsingResponse:
        return CutterParsingResponse(ctx_data.get()[self.var_name], args)


class TextArgumentCutter(Cutter, ABC):
    """
    Базовый катер текстового аргумента.
    Значение получается из строки, введенной пользователем.
    """

    async def get(self, message: Message, args: SafeList) -> CutterParsingResponse:
        """
        :raises RequiredArgumentNotPassed
        """
        if args[0] is None:
            raise RequiredArgumentNotPassed
        return await super(TextArgumentCutter, self).get(message, args)


class BaseTypeCutter(TextArgumentCutter, ABC):
    """
    Базовый катер текстового аргумента питоновского типа.
    Значение получается из строки, введенной пользователем.
    """

    # Тип данных
    # Должно быть изменено в наследуемом классе
    factory: ty.Any

    async def _get(self, message: Message, args: SafeList) -> CutterParsingResponse:
        return CutterParsingResponse(self.factory(args[0]), args[1:])


class HandlerParam(ty.NamedTuple):
    """
    Модель хранения параметра обработчика команды.
    """

    param_name: str  # Имя параметра
    cutter: Cutter  # Катер
    param_settings: Param  # Настройки параметра

    def __repr__(self):
        return f"<Param {self.param_name} cutter={self.cutter}>"

    def __format__(self, format_spec):
        """
        Вызывается при вставке экземпляра в строку методом str.format или f-строкой.
        :param format_spec: Модификатор.
            colored - Подготавливает строку к цветному выводу в консоль.
        """
        if format_spec == "colored":
            return (
                f"<e><</e>Param <e>{self.param_name}</e> "
                f"cutter={self.cutter:colored}<e>></e>"
            )
        return repr(self)


@dataclass
class Param:
    """
    Модель настроек параметра обработчика команды.
    Когда пользователь некорректно использует команду,
    пользователю дается описание некорректного аргумента.
    Params:
        name: Название аргумента (Для пользователя)
        description: Описание аргумента (Для пользователя)
        default: Значение по умолчанию
        default_factory: Фабрика значений по умолчанию
    """

    name: str | None = None
    description: str = ""
    default: ty.Any | None = None
    default_factory: ty.Callable[[], ty.Any] | None = None

    def __post_init__(self):
        if self.description:
            self.description = "\n" + self.description
