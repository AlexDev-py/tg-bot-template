from dataclasses import dataclass

from loguru import logger

from .db_type import DBType


@dataclass
class DBConfig:
    """
    Конфигурация подключения к базе данных.
    """

    db_type: DBType = None
    db_url: str = None
    db_path: str = None

    def create_url_config(self) -> str:
        """
        :return: Ссылка на базу данных.
        """
        if self.db_type in {DBType.mysql, DBType.postgres}:
            db_url = self.db_url
        elif self.db_type == DBType.sqlite:
            db_url = f"{self.db_type.value}://{self.db_path}"
        else:
            raise ValueError("DB_TYPE not mysql, sqlite or postgres")
        logger.debug(f"{db_url=}")
        return db_url
