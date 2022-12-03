from logging import Logger
from logging import getLogger
from typing import Coroutine
from typing import Optional
from typing import Sequence

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
        """
        Attempts to find a quest the provided name and add it to the list of currently accepted quests
        for the user

        Parameters
        ----------
        user: User
        quest_name: str

        Returns
        -------
        str: A success message with the provided quest name

        Raises
        ------
        QuestDNE: If no quest is found with the provided name
        QuestAlreadyAccepted: If the provided user has already accepted this quest
        """
        quest = await self._get_quest_by_name(quest_name)
        if not quest:
            raise QuestDNE(quest_name)

        if user in quest.users:
            raise QuestAlreadyAccepted(quest_name)

        quest.users.append(user)
        await self._repository.session.commit()
        return GOOD_LUCK_ADVENTURER.format(quest_name)

    async def complete_quest_if_available(self, user: User, quest_name: str) -> Quest:
        """
        Attempt to retrieve a quest for a quest and check that a user can complete it

        Parameters
        ----------
        user: User
        quest_name: str

        Returns
        -------
        Quest: The matching quest object

        Raises
        ------
        QuestDNE: If no quest is found with the provided name
        QuestNotAccepted: If the user has not accepted the provided quest
        """
        quest = await self._get_quest_by_name(quest_name)
        if not quest:
            raise QuestDNE(quest_name)

        if user not in quest.users:
            raise QuestNotAccepted(quest_name)

        return quest

    async def get_all_quests(self) -> Sequence[Quest]:
        quests = await self._repository.get_all()
        return quests


class ExperienceTransactionService(BaseService):
    _repository: BaseRepository[ExperienceTransaction]

    async def earn_xp_for_quest(self, user: User, quest: Quest) -> ExperienceTransaction:
        xp_transaction = await self._repository.create(user=user, quest=quest)
        return xp_transaction
