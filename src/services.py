from logging import Logger
from logging import getLogger
from typing import Optional

from sqlalchemy.orm import selectinload

from src.constants import GOOD_LUCK_ADVENTURER
from src.constants import QUEST_ALREADY_ACCEPTED
from src.constants import QUEST_DOES_NOT_EXIST
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
            QueryArgs(
                filter_list=[case_insensitive_str_compare(Quest.name, quest_name)],
                eager_options=[selectinload(Quest.users)],
            )
        )
        if not quest:
            return QUEST_DOES_NOT_EXIST

        if user in quest.users:
            return QUEST_ALREADY_ACCEPTED

        quest.users.append(user)
        await self._repository.session.commit()
        return GOOD_LUCK_ADVENTURER.format(quest_name)
