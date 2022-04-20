from logging import Logger
from logging import getLogger
from typing import Coroutine
from typing import Optional

from models import User
from repositories import QueryArgs
from repositories import UserRepository


class BaseService:
    def __init__(self) -> None:
        self.logger: Logger = getLogger(
            f"{__name__}.{self.__class__.__name__}",
        )


class UserService(BaseService):
    def __init__(self, user_repository: UserRepository):
        super().__init__()
        self._repository = user_repository

    def get_user_by_id(self, user_id: int) -> Coroutine[None, None, Optional[User]]:
        return self._repository.get_by_id(user_id)

    def get_user_by_discord_id(self, discord_id: int) -> Coroutine[None, None, Optional[User]]:
        return self._repository.get_first(QueryArgs(filter_dict=dict(discord_id=discord_id)))

    def create_user(self, discord_id: int) -> Coroutine[None, None, User]:
        return self._repository.create(discord_id=discord_id)
