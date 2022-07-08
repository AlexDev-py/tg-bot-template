from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode

from config import load_config
from models.config import Config
from utils.logger import logger, setup_logger

current_config = load_config()

bot = Bot(current_config.bot_token, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())


def setup(config: Config):
    setup_logger(config)

    logger.debug(f"As application dir using: {config.app_dir}")

    import filters
    import middlewares
    from utils import executor

    middlewares.setup(dp, config)
    filters.setup(dp, config)
    executor.setup(config)

    logger.debug("Configure handlers...")
    import handlers  # noqa: unused import
