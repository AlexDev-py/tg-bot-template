from __future__ import annotations

import asyncio
import typing as ty

from aiogram import Dispatcher
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled

if ty.TYPE_CHECKING:
    from aiogram.types import Message


class ThrottlingMiddleware(BaseMiddleware):
    """
    Middleware для контроля флуда.
    """

    def __init__(self, limit=1, key_prefix="antiflood_"):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def on_process_message(self, message: Message, *_):
        handler = current_handler.get()  # Получаем обработчик команды
        dispatcher = Dispatcher.get_current()
        if handler:
            # Если обработчик команды зарегистрирован, получаем настройку антифлуда
            limit = getattr(handler, "throttling_rate_limit", self.rate_limit)
            key = getattr(
                handler, "throttling_key", f"{self.prefix}_{handler.__name__}"
            )
        else:
            # Обработчика команды нет
            limit = self.rate_limit
            key = f"{self.prefix}_message"

        try:
            # Проверяем соблюдение лимита
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            # Нарушение
            await self.handle_throttled(message, t)
            raise CancelHandler()  # Не пропускаем событие дальше

    async def handle_throttled(self, message: Message, throttled: Throttled):
        """
        Уведомляет пользователя о превышение.
        Если команда уже заблокирована, то время блокировки прибавляется.
        """
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()
        if handler:
            key = getattr(
                handler, "throttling_key", f"{self.prefix}_{handler.__name__}"
            )
        else:
            key = f"{self.prefix}_message"

        # Определяем время блокировки команды
        delta = throttled.rate - throttled.delta

        # Уведомляем о превышении
        if throttled.exceeded_count <= 2:
            await self.send_message_about_throttled(message, throttled)

        # Блокируем
        await asyncio.sleep(delta)

        # Проверяем статус блокировки
        thr = await dispatcher.check_key(key)

        if thr.exceeded_count == throttled.exceeded_count:
            # Если это последнее сообщение с вызовом команды
            await dispatcher.release_key(key)
            await self.delete_message_about_throttled(message, throttled)

    @staticmethod
    async def send_message_about_throttled(
        message: Message, throttled: Throttled
    ) -> None:
        dispatcher = Dispatcher.get_current()
        msg = await message.reply("Команда временно заблокирована")
        msg_key = throttled.key + "_msg"

        bucket = (
            await dispatcher.storage.get_bucket(
                chat=message.chat.id, user=message.from_user.id
            )
        ) or dict()
        bucket[msg_key] = msg
        await dispatcher.storage.set_bucket(
            chat=message.chat.id, user=message.from_user.id, bucket=bucket
        )

    @staticmethod
    async def delete_message_about_throttled(
        message: Message, throttled: Throttled
    ) -> None:
        dispatcher = Dispatcher.get_current()
        msg_key = throttled.key + "_msg"
        bucket = (
            await dispatcher.storage.get_bucket(
                chat=message.chat.id, user=message.from_user.id
            )
        ) or dict()

        if msg := bucket.get(msg_key):
            await msg.delete()
            await dispatcher.release_key(msg_key)
