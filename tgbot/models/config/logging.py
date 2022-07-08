from dataclasses import dataclass

from loguru import logger

from .db_type import DBType


@dataclass
class LoggingConfig:
    """
    Конфигурация логирования.
    """

    logging_level: str = None

    logging_db_type: DBType = None
    logging_db_url: str = None
    logging_db_path: str = None

    def create_url_config(self) -> str:
        """
        :return: Ссылка на базу данных с логами.
        """
        if self.logging_db_type in {DBType.mysql, DBType.postgres}:
            logging_db_url = self.logging_db_url
        elif self.logging_db_type == DBType.sqlite:
            logging_db_url = f"{self.logging_db_type.value}://{self.logging_db_path}"
        else:
            raise ValueError("DB_TYPE not mysql, sqlite or postgres")
        logger.debug(f"{logging_db_url=}")
        return logging_db_url
