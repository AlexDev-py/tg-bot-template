from __future__ import annotations

import typing as ty
from datetime import timedelta

from aiogram.utils.exceptions import BadRequest
from loguru import logger

from config import moderation
from models.db import ModeratorEvent
from utils.exceptions import CantRestrict

if ty.TYPE_CHECKING:
    from aiogram import Bot
    from models.db import User, Chat
    from models.restriction import TypeRestriction


async def restrict(
    bot: Bot,
    chat: Chat,
    target: User,
    admin: User,
    duration: timedelta,
    comment: str,
    type_restriction: TypeRestriction,
) -> None:
    """
    Выдает ограничение пользователю.
    :param bot:
    :param chat:
    :param target: Получатель.
    :param admin: Администратор, использующий команду.
    :param duration: Длительность ограничения.
    :param comment: Комментарий.
    :param type_restriction: Тип ограничения.
    :return:
    """
    try:
        await moderation.action_for_restrict[type_restriction](
            bot,
            chat_id=chat.chat_id,
            user_id=target.user_id,
            until_date=duration,
        )
    except BadRequest as e:
        print(type(e))
        raise CantRestrict(
            origin_exception=e,
            text=e.text,
            user_id=target.user_id,
            chat_id=chat.chat_id,
            reason=comment,
            type_event=type_restriction.name,
        )
    else:
        # Сохраняем событие в бд.
        await ModeratorEvent.save_new_action(
            moderator=admin,
            user=target,
            chat=chat,
            type_restriction=type_restriction.name,
            duration=duration,
            comment=comment,
        )
        logger.opt(colors=True).log(
            "RESTRICTION",
            "User <e>{user}</e> restricted (<y>{type_restriction}</y>) "
            "by <e>{admin}</e> for <y>{duration}</y> in chat <e>{chat}</e>",
            user=target,
            type_restriction=type_restriction.name,
            admin=admin,
            duration=duration,
            chat=chat,
        )


async def un_restrict(bot: Bot, chat: Chat, target: User) -> None:
    """
    Снимает все ограничения с пользователя.
    Пользователю выдаются права по умолчанию, установленные в чате.
    :param bot:
    :param chat:
    :param target: Целевой пользователь.
    """
    try:
        # restrict in telegram
        await bot.restrict_chat_member(
            chat_id=chat.chat_id,
            user_id=target.user_id,
            permissions=(await bot.get_chat(chat.chat_id)).permissions,
        )
    except BadRequest as e:
        raise CantRestrict(
            origin_exception=e,
            text=e.text,
            user_id=target.user_id,
            chat_id=chat.chat_id,
            type_event=TypeRestriction.no_one.value,
        )
