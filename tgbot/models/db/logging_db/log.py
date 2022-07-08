import asyncio
from datetime import datetime

from tortoise import fields
from tortoise.models import Model


class Log(Model):
    """
    ОРМ модель логов.
    """

    id = fields.IntField(pk=True)
    level = fields.CharField(max_length=1, null=False)
    msg = fields.TextField()
    date = fields.DatetimeField()
    extra = fields.JSONField(null=True)

    class Meta:
        app = "logging"
        table = "logs"

    @classmethod
    def add(
        cls, *, level: str, msg: str, date: str | datetime, extra: dict | None = None
    ) -> None:
        """
        Запись лога в бд.
        :param level: Уровень.
        :param msg: Сообщение.
        :param date: Дата.
        :param extra: Дополнительные данные.
        """
        asyncio.tasks.ensure_future(
            cls.create(
                level=level,
                msg=msg,
                date=(
                    date
                    if isinstance(date, datetime)
                    else datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
                ),
                extra=extra,
            )
        )

    def __repr__(self):
        return f"[{self.level[0]} {self.date}]: {self.msg}"
