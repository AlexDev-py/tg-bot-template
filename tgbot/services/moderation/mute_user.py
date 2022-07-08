"""

Команды мута.

/mute
/unmute

"""

from aiogram.types import Message
from aiogram.utils.markdown import hbold

from models.db import User, Chat
from models.restriction import TypeRestriction
from utils.handler_params import command_handler, Param
from utils.handler_params.cutters import Timedelta
from utils.timedelta_functions import format_timedelta
from .restrict import restrict, un_restrict


@command_handler
async def mute_user(
    message: Message,
    chat: Chat,
    sender: User,
    target: User = Param("целевой пользователь"),
    duration: Timedelta = Param("длительность"),
    *,
    comment: str | None = Param("комментарий"),
) -> str:
    await restrict(
        bot=message.bot,
        chat=chat,
        target=target,
        admin=sender,
        duration=duration,
        comment=comment,
        type_restriction=TypeRestriction.mute,
    )

    return (
        f"{TypeRestriction.get_emoji(TypeRestriction.mute)} "
        f"Пользователь {target.mention_link} сможет {hbold('только читать')} сообщения "
        f"на протяжении {format_timedelta(duration)}"
    )


@command_handler
async def unmute_user(
    message: Message, chat: Chat, target: User = Param("целевой пользователь")
) -> str:
    await un_restrict(
        bot=message.bot,
        chat=chat,
        target=target,
    )

    return f"C пользователя {target.mention_link} сняты {hbold('все')} ограничения"
