from __future__ import annotations

import typing as ty

from aiogram.utils.markdown import hlink, quote_html
from tortoise import fields
from tortoise.exceptions import DoesNotExist
from tortoise.models import Model

if ty.TYPE_CHECKING:
    from aiogram.types import User as TgUser


class User(Model):
    """
    Орм модель пользователя.
    """

    id = fields.IntField(pk=True)
    user_id = fields.BigIntField(unique=True)
    first_name = fields.CharField(max_length=255, null=True)
    last_name = fields.CharField(max_length=255, null=True)
    username = fields.CharField(max_length=32, null=True)
    is_bot: bool = fields.BooleanField(null=True)

    class Meta:
        app = "tg"
        table = "users"

    @classmethod
    async def create_from_tg_user(cls, user_tg: TgUser) -> User:
        """
        Создает запись пользователя в бд.
        :param user_tg: Данные о пользователе, полученный от телеграма.
        :return: Созданный экземпляр User.
        """
        user = await cls.create(
            user_id=user_tg.id,
            first_name=user_tg.first_name,
            last_name=user_tg.last_name,
            username=user_tg.username,
            is_bot=user_tg.is_bot,
        )

        return user

    async def update_user_data(self, user_tg: TgUser) -> None:
        """
        Обновляет данные о пользователе в бд.
        :param user_tg: Данные о пользователе, полученный от телеграма.
        """
        changed = False

        if self.user_id is None and user_tg.id is not None:
            changed = True
            self.user_id = user_tg.id

        if user_tg.first_name is not None:
            if self.first_name != user_tg.first_name:
                changed = True
                self.first_name = user_tg.first_name

            if self.last_name != user_tg.last_name:
                changed = True
                self.last_name = user_tg.last_name

            if self.username != user_tg.username:
                changed = True
                self.username = user_tg.username

            if self.is_bot is None and user_tg.is_bot is not None:
                changed = True
                self.is_bot = user_tg.is_bot

        if changed:
            await self.save()

    @classmethod
    async def get_or_create_from_tg_user(cls, user_tg: TgUser) -> User:
        """
        Получает пользователя из бд.
        Если записи нет - создает.
        :param user_tg: Данные о чате, полученный от телеграма.
        :return: Экземпляр Chat.
        """
        if user_tg.id is None:
            try:
                return await cls.get(username__iexact=user_tg.username)
            except DoesNotExist:
                raise RuntimeError(f"User without user_id: {user_tg}")

        try:
            user = await cls.get(user_id=user_tg.id)
        except DoesNotExist:
            return await cls.create_from_tg_user(user_tg)
        else:
            await user.update_user_data(user_tg)
        return user

    @property
    def mention_link(self):
        return hlink(self.fullname, f"tg://user?id={self.user_id}")

    @property
    def mention_no_link(self):
        if self.username:
            rez = hlink(self.fullname, f"t.me/{self.username}")
        else:
            rez = quote_html(self.fullname)
        return rez

    @property
    def fullname(self):
        if self.last_name is not None:
            return " ".join((self.first_name, self.last_name))
        return self.first_name or self.username or str(self.user_id) or str(self.id)

    def to_dict(self):
        return dict(
            id=self.id,
            user_id=self.user_id,
            first_name=self.first_name,
            last_name=self.last_name,
            username=self.username,
            is_bot=self.is_bot,
        )

    def __repr__(self):
        rez = f"({self.fullname}) (id: {self.user_id})"
        if self.username:
            rez = f"@{self.username}" + rez
        return rez

    __str__ = __repr__
