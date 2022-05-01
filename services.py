from logging import Logger
from logging import getLogger
from typing import Optional

from helpers.sqlalchemy_helpers import QueryArgs
from models import User
from repositories import BaseRepository


class BaseService:
    def __init__(self) -> None:
        self.logger: Logger = getLogger(
            f"{__name__}.{self.__class__.__name__}",
        )


class UserService(BaseService):
    def __init__(self, user_repository: BaseRepository[User]):
        super().__init__()
        self._repository = user_repository

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        return await self._repository.get_by_id(user_id)

    async def get_user_by_discord_id(self, discord_id: int) -> Optional[User]:
        return await self._repository.get_first(QueryArgs(filter_dict=dict(discord_id=discord_id)))

    async def create_user(self, discord_id: int) -> User:
        return await self._repository.create(discord_id=discord_id)
