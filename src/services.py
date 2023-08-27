from dataclasses import dataclass
from dataclasses import field
from logging import Logger
from logging import getLogger

from src.helpers.sqlalchemy_helpers import QueryArgs
from src.models import User
from src.repositories import BaseRepository


@dataclass(frozen=True, kw_only=True)
class BaseService:
    logger: Logger = field(init=False)
    _repository: BaseRepository

    def __post_init__(self) -> None:
        object.__setattr__(self, "logger", getLogger(f"{__name__}.{self.__class__.__name__}"))


class UserService(BaseService):
    _repository: BaseRepository[User]

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self._repository.get_by_id(user_id)

    async def get_user_by_discord_id(self, discord_id: int) -> User | None:
        return await self._repository.get_first(QueryArgs(filter_dict={"discord_id": discord_id}))

    async def create_user(self, discord_id: int) -> User:
        user = User(discord_id=discord_id)
        await self._repository.add(user)
        return user
