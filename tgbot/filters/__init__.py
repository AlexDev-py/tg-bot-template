from __future__ import annotations

import typing as ty
from functools import partialmethod

from loguru import logger

if ty.TYPE_CHECKING:
    from aiogram import Dispatcher
    from models.config import Config


def setup(dispatcher: Dispatcher, config: Config):
    logger.debug("Configure filters...")
    from .superuser import IsSuperuserFilter

    text_messages = [
        dispatcher.message_handlers,
        dispatcher.edited_message_handlers,
        dispatcher.callback_query_handlers,
    ]
    IsSuperuserFilter.check = partialmethod(IsSuperuserFilter.check, config.superusers)

    dispatcher.filters_factory.bind(IsSuperuserFilter, event_handlers=text_messages)
