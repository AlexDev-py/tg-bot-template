from __future__ import annotations

import typing as ty

from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Chat as TgChat
from loguru import logger

if ty.TYPE_CHECKING:
    from aiogram.types import Message
    from models.db import User, Chat


class LoggingMiddleware(BaseMiddleware):
    """
    Middleware для логирования команд.
    """

    @staticmethod
    async def on_process_message(message: Message, data: dict):
        user: User = data["user"]
        chat: Chat | TgChat = data["chat"]
        command = message.text

        logger.opt(colors=True).log(
            "COMMAND",
            "User <y>{user}</y> in chat <y>{chat}</y> call command <e>{command}</e>",
            user=user,
            chat=(
                f"{chat['type']} chat (id: {chat['id']})"
                if isinstance(chat, TgChat)
                else chat
            ),
            command=command,
        )
