import os
from functools import lru_cache
from pathlib import Path

from models.config import Config
from .db import load_db_config
from .log import load_log_config
from .webhook import load_webhook_config


@lru_cache
def load_config() -> Config:
    app_dir: Path = Path(__file__).parent.parent.parent

    return Config(
        db=load_db_config(app_dir),
        webhook=load_webhook_config(),
        app_dir=app_dir,
        bot_token=os.getenv("BOT_TOKEN"),
        superusers=frozenset(map(int, os.getenv("SUPERUSERS", "0").split(","))),
        logging=load_log_config(app_dir=app_dir),
    )
