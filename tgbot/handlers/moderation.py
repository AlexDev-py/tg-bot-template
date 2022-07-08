from __future__ import annotations

import typing as ty

from aiogram.types import ChatType

from misc import dp
from services.moderation import mute_user, unmute_user
from utils.handler_params import set_usage_pattern
from utils.rate_limit import rate_limit
from utils.tg_permissions import UserHasPermissions, BotHasPermissions, Permission

if ty.TYPE_CHECKING:
    from aiogram.types import Message


@dp.message_handler(
    chat_type=[ChatType.GROUP, ChatType.SUPERGROUP],
    commands=["mute", "мут"],
    commands_prefix="/",
)
@rate_limit(10)
@UserHasPermissions(Permission.CAN_RESTRICT_MEMBERS)
@BotHasPermissions(Permission.CAN_RESTRICT_MEMBERS)
@set_usage_pattern("/mute <получатель> <длительность> [причина]")
async def mute_cmd_handler(message: Message):
    await message.reply(await mute_user(message))


@dp.message_handler(
    chat_type=[ChatType.GROUP, ChatType.SUPERGROUP],
    commands=["unmute", "анмут"],
    commands_prefix="/",
)
@rate_limit(10)
@UserHasPermissions(Permission.CAN_RESTRICT_MEMBERS)
@BotHasPermissions(Permission.CAN_RESTRICT_MEMBERS)
@set_usage_pattern("/unmute <получатель>")
async def unmute_cmd_handler(message: Message):
    await message.reply(await unmute_user(message))
