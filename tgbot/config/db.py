import os
from pathlib import Path

from models.config.db import DBConfig, DBType


def load_db_config(app_dir: Path) -> DBConfig:
    return DBConfig(
        db_type=DBType.from_str(os.getenv("DATABASE_TYPE", default='sqlite')),
        db_url=os.getenv("DATABASE_URL"),
        db_path=str(app_dir / os.getenv("DATABASE_PATH", default="mydatabase.sqlite"))
    )
