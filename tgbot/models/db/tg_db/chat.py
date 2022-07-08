from __future__ import annotations

import typing as ty
from enum import Enum

from tortoise import fields
from tortoise.exceptions import DoesNotExist
from tortoise.models import Model

if ty.TYPE_CHECKING:
    from aiogram.types import Chat as TgChat


class ChatType(str, Enum):
    """
    Типы чатов.
    """

    private = "private"
    group = "group"
    supergroup = "supergroup"
    channel = "channel"


class Chat(Model):
    """
    ОРМ модель чата.
    """

    id = fields.IntField(pk=True)
    chat_id = fields.BigIntField(null=False, unique=True)
    chat_type: ChatType = ty.cast(ChatType, fields.CharEnumField(ChatType))
    title = fields.CharField(max_length=255, null=True)

    rules_msg_id = fields.BigIntField(null=True)
    greeting_msg_id = fields.BigIntField(null=True)

    class Meta:
        app = "tg"
        table = "chats"

    @classmethod
    async def create_from_tg_chat(cls, chat: TgChat) -> Chat:
        """
        Создает запись чата в бд.
        :param chat: Данные о чате, полученный от телеграма.
        :return: Созданный экземпляр Chat.
        """
        chat = await cls.create(
            chat_id=chat.id,
            chat_type=chat.type,
            title=chat.title,
            username=chat.username,
        )
        return chat

    @classmethod
    async def get_or_create_from_tg_chat(cls, chat: TgChat) -> Chat:
        """
        Получает чат из бд.
        Если записи нет - создает.
        :param chat: Данные о чате, полученный от телеграма.
        :return: Экземпляр Chat.
        """
        try:
            chat = await cls.get(chat_id=chat.id)
        except DoesNotExist:
            chat = await cls.create_from_tg_chat(chat=chat)
        return chat

    def __repr__(self):
        return f'{self.chat_type} chat "{self.title}" ({self.chat_id})'

    __str__ = __repr__
