from unittest.mock import MagicMock
from unittest.mock import AsyncMock

import pytest

from src.constants import GOOD_LUCK_ADVENTURER
from src.quests.exceptions import MaxQuestCompletionReached
from src.quests.exceptions import QuestAlreadyAccepted
from src.quests.exceptions import QuestDNE
from src.quests.exceptions import QuestNotAccepted
from src.quests.services import QuestService


@pytest.mark.asyncio()
class TestQuestService:
    async def test_accept_quest_if_available(self, mocked_user, mock_container):
        # Arrange
        mock_quest_repository = AsyncMock(
            get_first=AsyncMock(return_value=MagicMock(users=[])), session=AsyncMock(commit=AsyncMock())
        )
        mock_user_quest_repo = AsyncMock(get_count=AsyncMock(return_value=0), add=AsyncMock())
        quest_service = QuestService(_repository=mock_quest_repository, _secondary_repository=mock_user_quest_repo)
        # Act
        res = await quest_service.accept_quest_if_available(mocked_user, "Quest title")
        # Assert
        assert res == GOOD_LUCK_ADVENTURER.format("Quest title")
        mock_user_quest_repo.add.assert_called()

    async def test_quest_dne(self, mocked_user, mock_container):
        # Arrange
        mock_quest_repository = AsyncMock(get_first=AsyncMock(return_value=None))
        quest_service = QuestService(_repository=mock_quest_repository, _secondary_repository=AsyncMock())
        # Act & Assert
        with pytest.raises(QuestDNE):
            await quest_service.accept_quest_if_available(mocked_user, "Quest title")

    async def test_quest_already_accepted(self, mocked_user, mock_container):
        # Arrange
        quest = MagicMock(users=[mocked_user])
        mock_quest_repository = AsyncMock(
            get_first=AsyncMock(return_value=quest), session=AsyncMock(commit=AsyncMock())
        )
        mock_user_quest_repo = AsyncMock(get_count=AsyncMock(return_value=1))
        quest_service = QuestService(_repository=mock_quest_repository, _secondary_repository=mock_user_quest_repo)
        # Act & Assert
        with pytest.raises(QuestAlreadyAccepted):
            await quest_service.accept_quest_if_available(mocked_user, "Quest title")

    @pytest.mark.parametrize("max_completion_count", [None, 2])
    async def test_quest_completed(self, mocked_user, mock_container, max_completion_count):
        # Arrange
        quest = MagicMock(users=[mocked_user], max_completion_count=max_completion_count)
        mock_quest_repository = AsyncMock(
            get_first=AsyncMock(return_value=quest), session=AsyncMock(commit=AsyncMock())
        )
        user_quest = MagicMock(user=mocked_user, quest=quest)
        mock_user_quest_repository = AsyncMock(
            get_count=AsyncMock(return_value=1), get_first=AsyncMock(return_value=user_quest)
        )
        quest_service = QuestService(
            _repository=mock_quest_repository, _secondary_repository=mock_user_quest_repository
        )
        # Act
        res = await quest_service.complete_quest_if_available(mocked_user, "Quest title")
        # Assert
        assert res == quest

    async def test_cannot_complete_nonexistent_quest(self, mocked_user, mock_container):
        # Arrange
        mock_quest_repository = AsyncMock(get_first=AsyncMock(return_value=None))
        quest_service = QuestService(_repository=mock_quest_repository, _secondary_repository=AsyncMock())
        # Act & Assert
        with pytest.raises(QuestDNE):
            await quest_service.complete_quest_if_available(mocked_user, "Quest Title")

    async def test_cannot_complete_unaccepted_quest(self, mocked_user, mock_container):
        # Arrange
        mock_quest_repository = AsyncMock(
            get_first=AsyncMock(return_value=MagicMock()), session=AsyncMock(commit=AsyncMock())
        )
        mock_user_quest_repo = AsyncMock(get_first=AsyncMock(return_value=None))
        quest_service = QuestService(_repository=mock_quest_repository, _secondary_repository=mock_user_quest_repo)
        # Act & Assert
        with pytest.raises(QuestNotAccepted):
            await quest_service.complete_quest_if_available(mocked_user, "Quest Title")

    async def test_max_completion_count_reached(self, mocked_user, mock_container):
        # Arrange
        quest = MagicMock(users=[mocked_user], max_completion_count=1, completed_users=[mocked_user])
        mock_quest_repository = AsyncMock(
            get_first=AsyncMock(return_value=quest), session=AsyncMock(commit=AsyncMock())
        )
        mock_user_quest_repository = AsyncMock(get_count=AsyncMock(return_value=1), get_first=AsyncMock())
        quest_service = QuestService(
            _repository=mock_quest_repository, _secondary_repository=mock_user_quest_repository
        )
        # Act & Assert
        with pytest.raises(MaxQuestCompletionReached):
            await quest_service.complete_quest_if_available(mocked_user, "Quest title")
