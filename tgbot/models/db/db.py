from functools import partial

from aiogram import Dispatcher
from aiogram.utils.executor import Executor
from loguru import logger
from tortoise import Tortoise, run_async

from models.config import Config
from .logging_db import __models__ as __logging_models__
from .tg_db import __models__ as __tg_models__


async def db_init(config: Config) -> None:
    """
    Подключение бд.
    :param config: Текущая конфигурация.
    """
    tg_db_url = config.db.create_url_config()
    logger.debug("Connecting to db {tg_db_url}", tg_db_url=tg_db_url)
    logging_db_url = config.logging.create_url_config()
    logger.debug(
        "Connecting to logging db {logging_db_url}", logging_db_url=logging_db_url
    )
    await Tortoise.init(
        {
            "connections": {
                "tg_db": tg_db_url,
                "logging_db": logging_db_url,
            },
            "apps": {
                "tg": {"models": __tg_models__, "default_connection": "tg_db"},
                "logging": {
                    "models": __logging_models__,
                    "default_connection": "logging_db",
                },
            },
        }
    )


async def on_startup(_: Dispatcher, config: Config) -> None:
    await db_init(config)


async def on_shutdown(_: Dispatcher) -> None:
    await Tortoise.close_connections()


def setup(executor: Executor, config: Config) -> None:
    """
    Устанавливаем обработчик запуска и остановки бота.
    :param executor: Исполнитель.
    :param config: Текущая конфигурация.
    """
    executor.on_startup(partial(on_startup, config=config))
    executor.on_shutdown(on_shutdown)


async def generate_schemas_db(config: Config) -> None:
    await db_init(config)
    await Tortoise.generate_schemas()


def generate_schemas(config: Config) -> None:
    run_async(generate_schemas_db(config))
