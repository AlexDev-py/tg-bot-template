from __future__ import annotations

import typing as ty

from aiogram import Dispatcher
from loguru import logger

from .config_middleware import ConfigMiddleware
from .db_middleware import DBMiddleware
from .logging_middleware import LoggingMiddleware
from .throttling import ThrottlingMiddleware

# from aiogram.contrib.middlewares.logging import LoggingMiddleware


if ty.TYPE_CHECKING:
    from models.config import Config


def setup(dispatcher: Dispatcher, config: Config):
    logger.debug("Configure middlewares...")
    dispatcher.middleware.setup(DBMiddleware())
    dispatcher.middleware.setup(ConfigMiddleware(config))
    dispatcher.middleware.setup(LoggingMiddleware())
    dispatcher.middleware.setup(ThrottlingMiddleware())
