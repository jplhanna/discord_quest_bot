from logging import Logger
from logging import getLogger

from src.helpers.sqlalchemy_helpers import QueryArgs
from src.models import User
from src.repositories import BaseRepository
from src.typeshed import RepositoryHandler


class BaseService:
    logger: Logger

    def __init__(self) -> None:
        self.logger = getLogger(f"{__name__}.{self.__class__.__name__}")


class SingleRepoService(BaseService):
    _repository: BaseRepository

    def __init__(self, repository: BaseRepository) -> None:
        super().__init__()
        self._repository = repository


class MultiRepoService(BaseService):
    _repositories: RepositoryHandler

    def __init__(self, **repositories: BaseRepository) -> None:
        super().__init__()
        self._repositories = RepositoryHandler(**repositories)


class UserService(SingleRepoService):
    _repository: BaseRepository[User]

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self._repository.get_by_id(user_id)

    async def get_user_by_discord_id(self, discord_id: int) -> User | None:
        return await self._repository.get_first(QueryArgs(filter_dict={"discord_id": discord_id}))

    async def create_user(self, discord_id: int) -> User:
        user = User(discord_id=discord_id)
        await self._repository.add(user)
        return user
