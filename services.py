from logging import Logger
from logging import getLogger
from typing import Optional

from sqlalchemy.engine import Connection

from models import User
from repositories import UserRepository


class BaseService:
    def __init__(self) -> None:
        self.logger: Logger = getLogger(
            f"{__name__}.{self.__class__.__name__}",
        )


class DataBaseService(BaseService):
    def __init__(self, database: Connection):
        super().__init__()
        self.database = database


class UserService(BaseService):
    def __init__(self, user_repository: UserRepository):
        super().__init__()
        self._repository = user_repository

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self._repository.get_by_id(user_id)

    def create_user(self, discord_id: int) -> User:
        return self._repository.create(discord_id=discord_id)
