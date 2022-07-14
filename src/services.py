from logging import Logger
from logging import getLogger
from typing import Optional

from src.helpers.sqlalchemy_helpers import QueryArgs
from src.helpers.sqlalchemy_helpers import case_insensitive_str_compare
from src.models import Quest
from src.models import User
from src.repositories import BaseRepository


class BaseService:
    def __init__(self, repository: BaseRepository) -> None:
        self.logger: Logger = getLogger(
            f"{__name__}.{self.__class__.__name__}",
        )
        self._repository = repository


class UserService(BaseService):
    _repository: BaseRepository[User]

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        return await self._repository.get_by_id(user_id)

    async def get_user_by_discord_id(self, discord_id: int) -> Optional[User]:
        return await self._repository.get_first(QueryArgs(filter_dict=dict(discord_id=discord_id)))

    async def create_user(self, discord_id: int) -> User:
        return await self._repository.create(discord_id=discord_id)


class QuestService(BaseService):
    _repository: BaseRepository[Quest]

    async def accept_quest_if_available(self, user: User, quest_name: str) -> str:
        quest = await self._repository.get_first(
            QueryArgs(filter_list=[case_insensitive_str_compare(Quest.name, quest_name)])
        )
        if not quest:
            return "This quest does not exist"

        # Is this right? Should I be pulling out the db into this layer?
        # TODO I don't this works because the user is from a different session/context
        #  need a way to have session available across the entirety of a discord command
        async with self._repository.session_factory() as session:
            user.quests.append(quest)
            await session.commit()
        return f"You have accepted {quest_name}! Good luck adventurer"
