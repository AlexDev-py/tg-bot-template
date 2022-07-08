"""

Модели конфигурации.

"""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .db import DBConfig
from .logging import LoggingConfig
from .webhook import WebhookConfig


@dataclass
class Config:
    """
    Конфигурация бота.
    """

    db: DBConfig
    webhook: WebhookConfig
    app_dir: Path
    bot_token: str
    superusers: Iterable[int]
    logging: LoggingConfig
    date_format: str = "%Y-%m-%d"
    date_time_format: str = "%Y-%m-%d %H:%M:%S.%f"
    time_to_cancel_actions: int = 60
    time_to_remove_temp_messages: int = 30


__all__ = [DBConfig, LoggingConfig, WebhookConfig]
