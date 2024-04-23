from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

from src.constants import GOOD_LUCK_ADVENTURER
from src.quests.exceptions import MaxQuestCompletionReached
from src.quests.exceptions import QuestAlreadyAccepted
from src.quests.exceptions import QuestDNE
from src.quests.exceptions import QuestNotAccepted
from src.quests.services import QuestService


@pytest.mark.asyncio()
@pytest.mark.usefixtures("mock_container")
class TestQuestService:
    async def test_accept_quest_if_available(self, user):
        # Arrange
        mock_quest_repository = AsyncMock(
            get_first=AsyncMock(return_value=MagicMock(users=[])), session=AsyncMock(commit=AsyncMock())
        )
        mock_user_quest_repo = AsyncMock(get_count=AsyncMock(return_value=0), add=AsyncMock())
        mock_repository_factory = MagicMock(side_effect=[mock_quest_repository, mock_user_quest_repo])
        quest_service = QuestService(
            repository_factory=mock_repository_factory, quest_model=MagicMock(), user_quest_model=MagicMock()
        )
        # Act
        res = await quest_service.accept_quest_if_available(user, "Quest title")
        # Assert
        assert res == GOOD_LUCK_ADVENTURER.format("Quest title")
        mock_user_quest_repo.add.assert_called()

    async def test_quest_dne(self, user):
        # Arrange
        mock_quest_repository = AsyncMock(get_first=AsyncMock(return_value=None))
        mock_repository_factory = MagicMock(side_effect=[mock_quest_repository, AsyncMock()])
        quest_service = QuestService(
            repository_factory=mock_repository_factory, quest_model=MagicMock(), user_quest_model=MagicMock()
        )
        # Act & Assert
        with pytest.raises(QuestDNE):
            await quest_service.accept_quest_if_available(user, "Quest title")

    async def test_quest_already_accepted(self, user):
        # Arrange
        quest = MagicMock(users=[user])
        mock_quest_repository = AsyncMock(
            get_first=AsyncMock(return_value=quest), session=AsyncMock(commit=AsyncMock())
        )
        mock_user_quest_repo = AsyncMock(get_count=AsyncMock(return_value=1))
        mock_repository_factory = MagicMock(side_effect=[mock_quest_repository, mock_user_quest_repo])
        quest_service = QuestService(
            repository_factory=mock_repository_factory, quest_model=MagicMock(), user_quest_model=MagicMock()
        )
        # Act & Assert
        with pytest.raises(QuestAlreadyAccepted):
            await quest_service.accept_quest_if_available(user, "Quest title")

    @pytest.mark.parametrize("max_completion_count", [None, 2])
    async def test_quest_completed(self, user, max_completion_count):
        # Arrange
        quest = MagicMock(users=[user], max_completion_count=max_completion_count)
        mock_quest_repository = AsyncMock(
            get_first=AsyncMock(return_value=quest), session=AsyncMock(commit=AsyncMock())
        )
        user_quest = MagicMock(user=user, quest=quest)
        mock_user_quest_repository = AsyncMock(
            get_count=AsyncMock(return_value=1), get_first=AsyncMock(return_value=user_quest)
        )
        mock_repository_factory = MagicMock(side_effect=[mock_quest_repository, mock_user_quest_repository])
        quest_service = QuestService(
            repository_factory=mock_repository_factory, quest_model=MagicMock(), user_quest_model=MagicMock()
        )
        # Act
        res = await quest_service.complete_quest_if_available(user, "Quest title")
        # Assert
        assert res == quest

    async def test_cannot_complete_nonexistent_quest(self, user):
        # Arrange
        mock_quest_repository = AsyncMock(get_first=AsyncMock(return_value=None))
        mock_repository_factory = MagicMock(side_effect=[mock_quest_repository, AsyncMock()])
        quest_service = QuestService(
            repository_factory=mock_repository_factory, quest_model=MagicMock(), user_quest_model=MagicMock()
        )
        # Act & Assert
        with pytest.raises(QuestDNE):
            await quest_service.complete_quest_if_available(user, "Quest Title")

    async def test_cannot_complete_unaccepted_quest(self, user):
        # Arrange
        mock_quest_repository = AsyncMock(
            get_first=AsyncMock(return_value=MagicMock()), session=AsyncMock(commit=AsyncMock())
        )
        mock_user_quest_repo = AsyncMock(get_first=AsyncMock(return_value=None))
        mock_repository_factory = MagicMock(side_effect=[mock_quest_repository, mock_user_quest_repo])
        quest_service = QuestService(
            repository_factory=mock_repository_factory, quest_model=MagicMock(), user_quest_model=MagicMock()
        )
        # Act & Assert
        with pytest.raises(QuestNotAccepted):
            await quest_service.complete_quest_if_available(user, "Quest Title")

    async def test_max_completion_count_reached(self, user):
        # Arrange
        quest = MagicMock(users=[user], max_completion_count=1, completed_users=[user])
        mock_quest_repository = AsyncMock(
            get_first=AsyncMock(return_value=quest), session=AsyncMock(commit=AsyncMock())
        )
        mock_user_quest_repository = AsyncMock(get_count=AsyncMock(return_value=1), get_first=AsyncMock())
        mock_repository_factory = MagicMock(side_effect=[mock_quest_repository, mock_user_quest_repository])
        quest_service = QuestService(
            repository_factory=mock_repository_factory, quest_model=MagicMock(), user_quest_model=MagicMock()
        )
        # Act & Assert
        with pytest.raises(MaxQuestCompletionReached):
            await quest_service.complete_quest_if_available(user, "Quest title")
