"""

Подготовка исполнителя к запуску бота.

"""

from functools import partial

from aiogram import Dispatcher
from aiogram.utils.executor import Executor
from loguru import logger

from misc import dp
from models.config import Config, WebhookConfig
from models.db import db

runner = Executor(dp)


async def on_startup_webhook(
    dispatcher: Dispatcher, webhook_config: WebhookConfig
) -> None:
    webhook_url = webhook_config.external_url
    logger.info("Configure Web-Hook URL to: {url}", url=webhook_url)
    await dispatcher.bot.set_webhook(webhook_url)


async def on_startup_pooling(_: Dispatcher) -> None:
    logger.info("Pooling started")


async def on_shutdown(_: Dispatcher) -> None:
    logger.info("Bot shutdown")


def setup(config: Config) -> None:
    """
    Подготовка исполнителя.
    :param config: Текущая конфигурация.
    """
    logger.debug("Configure executor...")

    db.setup(runner, config)  # Подключаем бд

    # Подключаем обработчики событий запуска и остановки бота
    runner.on_startup(
        partial(on_startup_webhook, webhook_config=config.webhook), polling=False
    )
    runner.on_startup(on_startup_pooling, webhook=False)
    runner.on_shutdown(on_shutdown)
