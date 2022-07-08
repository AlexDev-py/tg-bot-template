"""

Модуль, реализующий получение целевого пользователя.

"""

from __future__ import annotations

import typing as ty
from contextlib import suppress

from aiogram.types.user import User as TgUser
from loguru import logger
from tortoise.exceptions import MultipleObjectsReturned

from models.db import User

if ty.TYPE_CHECKING:
    from aiogram.types import Message
    from utils.safe_list import SafeList


def get_target_user(
    message: Message,
    args: SafeList | None = None,
    can_be_bot: bool = False,
) -> tuple[TgUser, SafeList | None] | None:
    """
    Получает целевого пользователя.
    :param message:
    :param args: Аргументы команды.
    :param can_be_bot: Обрабатывать ли ботов.
    :return: Целевой пользователь или None.
    """
    target_user = get_replied_user(message)
    if has_target_user(target_user, can_be_bot):
        return target_user, args

    target_user = get_mentioned_user(message, args)
    if has_target_user(target_user[0], can_be_bot):
        return target_user

    target_user = get_id_user(message, args)
    if has_target_user(target_user, can_be_bot):
        return target_user

    return None


def has_target_user(target_user: TgUser, can_be_bot: bool) -> True | False:
    """
    :return: True, если target_user существует и не бот
    """
    if target_user is None:
        return False
    if not can_be_bot and target_user.is_bot:
        return False

    return True


def get_mentioned_user(
    message: Message, args: SafeList | None = None
) -> tuple[TgUser | None, SafeList | None]:
    """
    Пытается получить пользователя из упоминания.
    """
    possible_mentioned_text = message.text or message.caption
    if not possible_mentioned_text:
        return None, args

    entities = message.entities or message.caption_entities
    if not entities:
        return None, args

    for ent in entities:
        if ent.type == "text_mention":
            if args is not None:
                args = args[len(ent.get_text(message.text)) :]
            return ent.user, args
        elif ent.type == "mention":
            username = ent.get_text(message.text).lstrip("@")
            if args is not None:
                args = args[1:]
            return TgUser(username=username), args
    return None, args


def get_replied_user(message: Message) -> TgUser | None:
    """
    Пытается получить пользователя из пересланного сообщения.
    """
    if message.reply_to_message:
        return message.reply_to_message.from_user


def get_id_user(message: Message, args: SafeList | None = None) -> TgUser | None:
    """
    Пытается получить пользователя по id из аргументов команды.
    """
    args: SafeList | str = args or message.get_args() or ""
    args: list[str] = [args[0]] if isinstance(args, list) else args.lower().split()

    for word in args:
        if word.startswith("id"):
            with suppress(ValueError):
                user_id = int(word.removeprefix("id"))
                return TgUser(id=user_id)


def is_bot_username(username: str):
    """
    this function deprecated. user can use username
    like @alice_bot and it don't say that it is bot
    """
    return username is not None and username[-3:] == "bot"


async def get_db_user_by_tg_user(target: TgUser) -> User:
    exception: Exception
    try:
        target_user = await User.get_or_create_from_tg_user(target)
    except MultipleObjectsReturned as e:
        logger.warning(
            "Strange, multiple username? chek id={id}, username={username}",
            id=target.id,
            username=target.username,
        )
        exception = e
    # In target can be user with only username
    except RuntimeError as e:
        exception = e
    else:
        return target_user

    raise exception
