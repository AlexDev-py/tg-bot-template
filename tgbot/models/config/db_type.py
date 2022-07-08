from __future__ import annotations

from enum import Enum


class DBType(Enum):
    """
    Типы баз данных.
    """

    mysql = "mysql"
    postgres = "postgres"
    sqlite = "sqlite"

    @classmethod
    def from_str(cls, value: str) -> DBType:
        try:
            return cls.__dict__["_member_map_"][value]
        except KeyError as err:
            raise KeyError(f"{value} DB type is not supported") from err
