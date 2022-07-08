import os
from pathlib import Path

from models.config.logging import LoggingConfig, DBType


def load_log_config(app_dir: Path) -> LoggingConfig:
    return LoggingConfig(
        logging_level=os.getenv("LOGGING_LEVEL", default="INFO"),
        logging_db_type=DBType.from_str(
            os.getenv("LOGGING_DATABASE_TYPE", default="sqlite")
        ),
        logging_db_url=os.getenv("LOGGING_DATABASE_URL"),
        logging_db_path=str(
            app_dir / os.getenv("LOGGING_DATABASE_PATH", default="logs.sqlite")
        ),
    )
