"""

Настройка логгера.
Используется loguru: https://github.com/Delgan/loguru

"""

from __future__ import annotations

import re
import sys
import typing as ty
from logging import Handler

from loguru import logger

from models.db import Log

if ty.TYPE_CHECKING:
    from logging import LogRecord
    from models.config import Config


def formatter(_) -> str:
    """
    Формат вывода логов.
    [{level.name[0]} {time:YYYY-MM-DD HH:mm:ss.SSS}]: {message}\n{exception}
    """
    return (
        "<lvl><n>["
        "{level.name[0]} "
        "</n></lvl><c>{time:YYYY-MM-DD HH:mm:ss.SSS}</c><lvl><n>"
        "]</n></lvl>"
        ": <lvl><n>{message}</n></lvl>\n{exception}"
    )


def setup_stdout_logger(config: Config) -> None:
    """
    Логер, выводящий записи в консоль.
    """
    logger.add(
        sys.stdout,
        format=formatter,
        level=config.logging.logging_level,
    )


def setup_db_logger() -> None:
    """
    Логер, сохраняющий логи в бд.
    """
    logger.add(
        DBLoggerHandler(),
        format=formatter,
        level="INFO",  # В бд не будет TRACE и DEBUG логов
    )


def update_logging_level(sink: ty.Any, level: str) -> None:
    """
    Изменение уровня логирования.
    :param sink: Логер.
    :param level: Уровень.
    """
    logger.configure(handlers=[dict(sink=sink, level=level)])


def update_stdout_logging_level(level: str) -> None:
    """
    Изменение уровня логирования в консоль.
    :param level: Уровень.
    """
    update_logging_level(sys.stdout, level)


def update_db_logging_level(level: str) -> None:
    """
    Изменение уровня логирования в бд.
    :param level: Уровень.
    """
    update_logging_level(DBLoggerHandler, level)


class DBLoggerHandler(Handler):
    """
    БД логер.
    """

    def emit(self, record: LogRecord) -> None:
        message = record.getMessage().strip()
        if match := re.fullmatch(
            r"\[(?P<lvl>.+?) (?P<date>.+?)]: (?P<msg>.+)", message, flags=re.DOTALL
        ):
            level, date, msg = map(
                str.strip, (match.group("lvl"), match.group("date"), match.group("msg"))
            )
            extra = record.extra.get("extra") if hasattr(record, "extra") else None
            Log.add(level=level, msg=msg, date=date, extra=extra)


def setup_logger(config) -> None:
    """
    Настройка логеров.
    :param config: Текущая конфигурация.
    """
    # Удаление настроек логгера по умолчанию
    logger.remove(0)

    setup_stdout_logger(config)
    setup_db_logger()

    # Настройка цветов и создание новых уровней логирования
    logger.level("DEBUG", color="<lk>")
    logger.level("TRACE", color="<lk>")

    logger.level("COMMAND", no=20, color="<n>")
    logger.level("ACTION", no=20, color="<lw>")
    logger.level("BUTTON", no=20, color="<e>")
    logger.level("RESTRICTION", no=20, color="<le>")
