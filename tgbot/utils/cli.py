"""

Консольный запуск бота.
Парсинг аргументов командной строки.

"""

from __future__ import annotations

import argparse
import typing as ty

from loguru import logger

if ty.TYPE_CHECKING:
    from models.config import Config


def create_parser():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "-w",
        "--webhook",
        action="store_const",
        const=True,
        help="Запуск бота с помощью WebHook. По умолчанию используется pooling",
    )
    arg_parser.add_argument(
        "-su",
        "--skip_updates",
        action="store_const",
        const=True,
        help="Пропустить не обработанные события",
    )
    return arg_parser


def cli(config: Config, webhook: bool | None = None, skip_updates: bool | None = None):
    parser = create_parser()
    namespace = parser.parse_args()

    import misc
    from utils.executor import runner

    misc.setup(config)
    if namespace.webhook or webhook:
        logger.debug("starting webhook...")
        runner.start_webhook(**config.webhook.listener_kwargs)
    else:
        logger.debug("starting polling...")
        runner.skip_updates = namespace.skip_updates or skip_updates
        runner.start_polling(reset_webhook=True)
