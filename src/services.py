from logging import Logger
from logging import getLogger
from typing import Coroutine
from typing import Optional

from sqlalchemy.orm import selectinload

from src.constants import GOOD_LUCK_ADVENTURER
from src.exceptions import QuestAlreadyAccepted
from src.exceptions import QuestDNE
from src.exceptions import QuestNotAccepted
from src.helpers.sqlalchemy_helpers import QueryArgs
from src.helpers.sqlalchemy_helpers import case_insensitive_str_compare
from src.models import ExperienceTransaction
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

    def _get_quest_by_name(self, quest_name: str) -> Coroutine[None, None, Optional[Quest]]:
        return self._repository.get_first(
            QueryArgs(
                filter_list=[case_insensitive_str_compare(Quest.name, quest_name)],
                eager_options=[selectinload(Quest.users)],
            )
        )

    async def accept_quest_if_available(self, user: User, quest_name: str) -> str:
        quest = await self._get_quest_by_name(quest_name)
        if not quest:
            raise QuestDNE(quest_name)

        if user in quest.users:
            raise QuestAlreadyAccepted(quest_name)

        quest.users.append(user)
        await self._repository.session.commit()
        return GOOD_LUCK_ADVENTURER.format(quest_name)

    async def complete_quest_if_available(self, user: User, quest_name: str) -> Quest:
        quest = await self._get_quest_by_name(quest_name)
        if not quest:
            raise QuestDNE(quest_name)

        if user not in quest.users:
            raise QuestNotAccepted(quest_name)

        return quest

    async def get_all_quests(self) -> list[Quest]:
        quests = await self._repository.get_all()
        return quests


class ExperienceTransactionService(BaseService):
    _repository: BaseRepository[ExperienceTransaction]

    async def earn_xp_for_quest(self, user: User, quest: Quest) -> ExperienceTransaction:
        xp_transaction = await self._repository.create(user=user, quest=quest)
        return xp_transaction
