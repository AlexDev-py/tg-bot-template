"""

Модуль, реализующий удаление сообщений и клавиатуры.

"""

import asyncio
from contextlib import suppress

from aiogram import types
from aiogram.utils.exceptions import (
    MessageToEditNotFound,
    MessageCantBeEdited,
    MessageCantBeDeleted,
    MessageToDeleteNotFound,
)


async def remove_kb(message: types.Message, sleep_time: int = 0) -> None:
    """
    Закрывает клавиатуру.
    :param message:
    :param sleep_time: Задержка до удаления.
    """
    await asyncio.sleep(sleep_time)
    with suppress(MessageToEditNotFound, MessageCantBeEdited):
        await message.edit_reply_markup()


async def delete_message(message: types.Message, sleep_time: int = 0) -> None:
    """
    Удаляет сообщение.
    :param message:
    :param sleep_time: Задержка до удаления.
    """
    await asyncio.sleep(sleep_time)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()
