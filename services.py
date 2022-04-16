from logging import Logger
from logging import getLogger


class BaseService:
    def __init__(self) -> None:
        self.logger: Logger = getLogger(
            f"{__name__}.{self.__class__.__name__}",
        )
