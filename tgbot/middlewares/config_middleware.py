from __future__ import annotations

import typing as ty

from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram.types.base import TelegramObject

if ty.TYPE_CHECKING:
    from models.config import Config


class ConfigMiddleware(LifetimeControllerMiddleware):
    def __init__(self, config: Config):
        super(ConfigMiddleware, self).__init__()
        self.config = config

    async def pre_process(self, obj: TelegramObject, data: dict, *args):
        data["config"]: Config = self.config
