from __future__ import annotations

import typing as ty

from misc import dp
from services.mini_games import choice, infa, random_num
from utils.handler_params import set_usage_pattern
from utils.rate_limit import rate_limit

if ty.TYPE_CHECKING:
    from aiogram.types import Message


@dp.message_handler(commands=["выбери", "choice"])
@rate_limit(2)
@set_usage_pattern("/выбери <аргумент> или <аргумент> или ...")
async def choice_handler(message: Message):
    await message.reply(await choice(message))


@dp.message_handler(commands="инфа")
@rate_limit(2)
@set_usage_pattern("/инфа <действие>")
async def choice_handler(message: Message):
    await message.reply(await infa(message))


@dp.message_handler(commands=["рандом", "random"])
@rate_limit(2)
@set_usage_pattern("/рандом [минимум] <максимум>")
async def choice_handler(message: Message):
    await message.reply(await random_num(message))
