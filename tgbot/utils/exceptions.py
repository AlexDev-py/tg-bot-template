"""

Исключения, вызывающиеся и обрабатывающиеся во время работы.

"""

import typing as ty

from aiogram.dispatcher.handler import current_handler


class CommandError(Exception):
    """
    Базовое исключение.
    """

    def __init__(
        self,
        text: str | None = None,
        user_id: int | None = None,
        chat_id: int | None = None,
        origin_exception: Exception | None = None,
        *args,
    ):
        """
        :param text: Текст ошибки.
        :param user_id: ID пользователя, вызвавшего событие.
        :param chat_id: ID чата, в котором произошло событие.
        :param origin_exception: Исключение, которое произошло до этого.
        :param args:
        """
        super(CommandError, self).__init__(text, args)
        self.text = text
        self.user_id = user_id
        self.chat_id = chat_id
        self.origin_exception = origin_exception

        if self.text is None and self.origin_exception is not None:
            self.text = str(self.origin_exception)

    def __repr__(self):
        text = f"{self.__class__.__name__}: {self.text}"
        if self.user_id is not None:
            text += f", by user {self.user_id} "
        if self.chat_id is not None:
            text += f"in chat {self.chat_id}"
        if self.origin_exception is not None:
            text += (
                ", origin exception: "
                f"{type(self.origin_exception).__name__}: {self.origin_exception}"
            )
        return text


# TimedeltaParseError


class TimedeltaParseError(CommandError):
    """
    Ошибка парсинга временного отрезка из текста.
    """


class ToLongDuration(TimedeltaParseError):
    """
    Временной отрезок слишком большой.
    """


class InvalidFormatDuration(TimedeltaParseError):
    """
    Невозможно распознать временной отрезок.
    """


# ParamsError


class ParamsError(CommandError):
    """
    Ошибка парсинга параметров команды.
    """


class RequiredArgumentNotPassed(ParamsError):
    """
    Обязательный аргумент не передан.
    """


class InvalidArgumentsError(ParamsError):
    """
    Некорректный аргумент.
    """

    def __init__(
        self, explanation: str | None = None, *, handler: ty.Any | None = None
    ):
        """
        :param explanation: Дополнительная информация.
        :param handler: Обработчик команды.
        """
        self.explanation: str = f"\n{explanation.strip()}" if explanation else ""
        self.handler = handler or current_handler.get()


# ModerationError


class ModerationError(CommandError):
    """
    Ошибка модерации.
    """

    def __init__(self, reason: str = None, type_event: str = None, *args, **kwargs):
        """
        :param reason: Причина ограничения.
        :param type_event: Тип ограничения.
        :param args:
        :param kwargs:
        """
        super(ModerationError, self).__init__(*args, **kwargs)
        self.reason = reason
        self.type_event = type_event


class CantRestrict(ModerationError):
    """
    Невозможно ограничить пользователя.
    """
