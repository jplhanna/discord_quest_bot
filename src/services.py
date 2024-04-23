from collections.abc import Callable
from logging import Logger
from logging import getLogger

from src.helpers.sqlalchemy_helpers import QueryArgs
from src.models import User
from src.repositories import BaseRepository
from src.typeshed import BaseModelType
from src.typeshed import RepositoryHandler


class BaseService:
    logger: Logger

    def __init__(self) -> None:
        self.logger = getLogger(f"{__name__}.{self.__class__.__name__}")


class SingleRepoService(BaseService):
    _repository: BaseRepository

    def __init__(
        self,
        repository_factory: Callable[[type[BaseModelType]], BaseRepository[BaseModelType]],
        model: type[BaseModelType],
    ) -> None:
        super().__init__()
        self._repository = repository_factory(model)


class MultiRepoService(BaseService):
    _repositories: RepositoryHandler

    def __init__(
        self,
        repository_factory: Callable[[type[BaseModelType]], BaseRepository[BaseModelType]],
        **models: type[BaseModelType],
    ) -> None:
        super().__init__()
        self._repositories = RepositoryHandler(repository_factory, **models)


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
