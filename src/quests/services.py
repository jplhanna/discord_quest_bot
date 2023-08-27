from collections.abc import Coroutine
from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy.orm import selectinload

from src.constants import GOOD_LUCK_ADVENTURER
from src.helpers.sqlalchemy_helpers import QueryArgs
from src.helpers.sqlalchemy_helpers import case_insensitive_str_compare
from src.models import User
from src.quests import ExperienceTransaction
from src.quests import Quest
from src.quests.exceptions import MaxQuestCompletionReached
from src.quests.exceptions import QuestAlreadyAccepted
from src.quests.exceptions import QuestDNE
from src.quests.exceptions import QuestNotAccepted
from src.quests.models import UserQuest
from src.repositories import BaseRepository
from src.services import BaseService


@dataclass(frozen=True)
class QuestService(BaseService):
    _repository: BaseRepository[Quest]
    _secondary_repository: BaseRepository[UserQuest]

    def _get_quest_by_name(self, quest_name: str) -> Coroutine[None, None, Quest | None]:
        return self._repository.get_first(
            QueryArgs(
                filter_list=[case_insensitive_str_compare(Quest.name, quest_name)],
                eager_options=[selectinload(Quest.users)],
            )
        )

    @staticmethod
    def _get_uncompleted_query_count_args(quest: Quest, user: User) -> QueryArgs:
        return QueryArgs(filter_dict={"user": user, "quest": quest, "completed": False})

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

        if await self._secondary_repository.get_count(self._get_uncompleted_query_count_args(quest, user)) >= 1:
            raise QuestAlreadyAccepted(quest)

        user_quest = UserQuest(user=user, quest=quest)  # type: ignore[call-arg]
        await self._secondary_repository.add(user_quest)
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

        active_user_quest = await self._secondary_repository.get_first(
            self._get_uncompleted_query_count_args(quest, user)
        )

        if not active_user_quest:
            raise QuestNotAccepted(quest)

        completed_quests_args = QueryArgs(filter_dict={"quest": quest, "user": user, "completed": True})

        if (
            quest.max_completion_count
            and await self._secondary_repository.get_count(completed_quests_args) >= quest.max_completion_count
        ):
            raise MaxQuestCompletionReached(quest)

        active_user_quest.mark_complete()
        await self._repository.session.commit()

        return quest

    async def get_all_quests(self) -> Sequence[Quest]:
        return await self._repository.get_all()


class ExperienceTransactionService(BaseService):
    _repository: BaseRepository[ExperienceTransaction]

    async def earn_xp_for_quest(self, user: User, quest: Quest) -> ExperienceTransaction:
        xp_transaction = ExperienceTransaction(user=user, quest=quest)  # type: ignore[call-arg]
        await self._repository.add(xp_transaction)
        return xp_transaction
