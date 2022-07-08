"""

Модуль, содержащий функции для парсинга временного отрезка из сообщения.

"""

from __future__ import annotations

import re
import typing as ty
from datetime import timedelta

from utils.exceptions import ToLongDuration, InvalidFormatDuration

if ty.TYPE_CHECKING:
    from re import Match

MODIFIERS = {
    ("y", "year", "years", "г", "год", "лет"): timedelta(
        days=365
    ),  # простим один день если кому-то попадётся високосный
    ("w", "week", "weeks", "н", "нд", "неделя", "недели", "недель"): timedelta(weeks=1),
    ("d", "day", "days", "д", "дн", "день", "дня", "дней"): timedelta(days=1),
    ("h", "hour", "hours", "ч", "час", "часа", "часов"): timedelta(hours=1),
    ("m", "minutes", "minutes", "м", "мин", "минута", "минуты", "минут"): timedelta(
        minutes=1
    ),
    ("s", "second", "seconds", "с", "сек", "секунда", "секунды", "секунд"): timedelta(
        seconds=1
    ),
}
ALL_MODIFIER = "|".join("|".join(_) for _ in MODIFIERS.keys())
PATTERN = re.compile(rf"(?P<value>\d+)\s?(?P<modifier>{ALL_MODIFIER})")
LINE_PATTERN = re.compile(rf"^(\d+\s?({ALL_MODIFIER})\s?)+$")


def _get_modifier_value(modifier: str) -> timedelta:
    for modifiers_group in MODIFIERS:
        if modifier in modifiers_group:
            return MODIFIERS[modifiers_group]


def parse_timedelta(value: str) -> tuple[timedelta, Match]:
    """
    Парсинг временного отрезка.
    :param value: Строка.
    :return: Временной отрезок и заданная строка.
    """
    # Подходит ли данная строка под шаблон временного отрезка
    match = LINE_PATTERN.match(value)
    if not match:
        raise InvalidFormatDuration(f"Некорректный формат времени: {value}")

    try:
        result = timedelta()
        for match in PATTERN.finditer(value):  # Парсинг всех указателей времени
            value, modifier = match.groups()

            result += int(value) * _get_modifier_value(modifier)
    except OverflowError as e:
        raise ToLongDuration("Временной отрезок слишком большой", origin_exception=e)

    return result, match


def parse_timedelta_from_text(
    text_duration: str,
) -> tuple[timedelta, Match] | None:
    """
    Гибкий парсинг временного отрезка их строки, введенной пользователем.
    :param text_duration: Данные от пользователя.
    """
    if not text_duration:
        return None

    # Разбираем текст на аргументы
    args = text_duration.split()
    current_line = ""
    last = None
    errors = 0

    # Добавляем к строке следующую часть и пробудем парсить из нее время
    for arg in args:
        current_line += " " + arg
        try:
            last = parse_timedelta(current_line.strip())
            errors = 0
        except InvalidFormatDuration:
            errors += 1
            if errors == 3:  # Если возникло 3 ошибки подряд
                break

    if last is None:  # Если в итоге не получилось найти время
        raise InvalidFormatDuration

    duration, match = last
    if duration <= timedelta(seconds=30):  # Минимальный временной отрезок
        return timedelta(seconds=30), match
    return duration, match


def format_timedelta(td: timedelta) -> str:
    """
    Приводит временной отрезок в человеко-читаемый вид.
    :param td: Временной отрезок.
    :return: Строка
    """
    rez = ""
    days = td.days
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    seconds = td.seconds % 60
    if days == 0 and td.seconds == 0:
        return "0 сек."
    if days > 0:
        rez += f"{days} дн. "
    if hours > 0:
        rez += f"{hours} ч. "
    if minutes > 0:
        rez += f"{minutes} мин. "
    if seconds > 0:
        rez += f"{seconds} сек. "
    return rez.strip()
