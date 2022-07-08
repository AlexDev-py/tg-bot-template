from __future__ import annotations

from datetime import timedelta, datetime

from aiogram.utils.markdown import quote_html
from tortoise import fields
from tortoise.models import Model

from models.restriction import TypeRestriction
from utils.timedelta_functions import format_timedelta
from . import Chat, User


class ModeratorEvent(Model):
    """
    Журнал аудита.
    """

    id = fields.IntField(pk=True, source_field="id")
    moderator: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "tg.User", related_name="my_moderator_events"
    )
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "tg.User", related_name="my_restriction_events"
    )
    chat: fields.ForeignKeyRelation[Chat] = fields.ForeignKeyField(
        "tg.Chat", related_name="moderator_events"
    )
    date: datetime = fields.DatetimeField(auto_now=True, null=False)
    type_restriction: str = fields.CharField(max_length=20)
    timedelta_restriction: timedelta = fields.TimeDeltaField(null=True)
    comment: str = fields.TextField(null=True)

    class Meta:
        app = "tg"
        table = "moderator_events"

    def __repr__(self):
        return (
            f"ModeratorEvent {self.id=} from {self.moderator.id} to {self.user.id}, "
            f"{self.date=}, {self.type_restriction=} {self.timedelta_restriction=}"
        )

    @classmethod
    async def save_new_action(
        cls,
        moderator: User,
        user: User,
        chat: Chat,
        type_restriction: str,
        duration: timedelta = None,
        comment: str = "",
    ) -> ModeratorEvent:
        """
        Создание новой записи.
        :param moderator: Инициатор действия.
        :param user: Целевой пользователь.
        :param chat: Чат.
        :param type_restriction: Тип ограничения.
        :param duration: Продолжительность ограничения.
        :param comment: Комментарий модератора.
        :return: Созданный экземпляр ModeratorEvent.
        """
        moderator_event = ModeratorEvent(
            moderator=moderator,
            user=user,
            chat=chat,
            type_restriction=type_restriction,
            timedelta_restriction=duration,
            comment=comment,
        )
        await moderator_event.save()
        return moderator_event

    @classmethod
    async def get_last_by_user(
        cls, user: User, chat: Chat, limit: int = 10
    ) -> list[ModeratorEvent]:
        """
        Возвращает последние `limit` записей касающихся пользователя `user`.
        :param user: Целевой пользователь.
        :param chat: Чат.
        :param limit: Кол-во записей.
        :return: Список экземпляров ModeratorEvent.
        """
        return (
            await cls.filter(user=user, chat=chat)
            .order_by("-date")
            .limit(limit)
            .prefetch_related("moderator")
            .all()
        )

    def format_event(self, date_format: str) -> str:
        rez = (
            f"{self.date.date().strftime(date_format)} "
            f"{TypeRestriction[self.type_restriction].get_emoji()}{self.type_restriction} "
        )

        if self.timedelta_restriction:
            rez += f"{format_timedelta(self.timedelta_restriction)} "

        rez += f"от {self.moderator.mention_no_link}"

        if self.comment:
            rez += f' "{quote_html(self.comment)}"'
        return rez
