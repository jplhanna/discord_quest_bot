from logging import Logger
from logging import getLogger

from sqlalchemy.engine import Connection


class BaseService:
    def __init__(self) -> None:
        self.logger: Logger = getLogger(
            f"{__name__}.{self.__class__.__name__}",
        )


class DataBaseService:
    def __init__(self, database: Connection):
        self.database = database
