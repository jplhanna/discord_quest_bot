from unittest.mock import MagicMock

import pytest
from asynctest import CoroutineMock
from asynctest import MagicMock as AsyncMagicMock

from src.constants import GOOD_LUCK_ADVENTURER
from src.exceptions import MaxQuestCompletionReached
from src.exceptions import QuestAlreadyAccepted
from src.exceptions import QuestDNE
from src.exceptions import QuestNotAccepted
from src.services import QuestService


@pytest.mark.asyncio()
class TestQuestService:
    async def test_accept_quest_if_available(self, mocked_user, mock_container):
        # Arrange
        mock_quest_repository = AsyncMagicMock(
            get_first=CoroutineMock(return_value=MagicMock(users=[])), session=AsyncMagicMock(commit=CoroutineMock())
        )
        quest_service = QuestService(repository=mock_quest_repository)
        # Act
        res = await quest_service.accept_quest_if_available(mocked_user, "Quest title")
        # Assert
        assert res == GOOD_LUCK_ADVENTURER.format("Quest title")

    async def test_quest_dne(self, mocked_user, mock_container):
        # Arrange
        mock_quest_repository = AsyncMagicMock(get_first=CoroutineMock(return_value=None))
        quest_service = QuestService(repository=mock_quest_repository)
        # Act & Assert
        with pytest.raises(QuestDNE):
            await quest_service.accept_quest_if_available(mocked_user, "Quest title")

    async def test_quest_already_accepted(self, mocked_user, mock_container):
        # Arrange
        quest = MagicMock(users=[mocked_user])
        mock_quest_repository = AsyncMagicMock(
            get_first=CoroutineMock(return_value=quest), session=AsyncMagicMock(commit=CoroutineMock())
        )
        quest_service = QuestService(repository=mock_quest_repository)
        # Act & Assert
        with pytest.raises(QuestAlreadyAccepted):
            await quest_service.accept_quest_if_available(mocked_user, "Quest title")

    @pytest.mark.parametrize("max_completion_count", [None, 2])
    async def test_quest_completed(self, mocked_user, mock_container, max_completion_count):
        # Arrange
        quest = MagicMock(users=[mocked_user], max_completion_count=max_completion_count, completed_users=[mocked_user])
        mock_quest_repository = AsyncMagicMock(
            get_first=CoroutineMock(return_value=quest, session=AsyncMagicMock(commit=CoroutineMock()))
        )
        quest_service = QuestService(repository=mock_quest_repository)
        # Act
        res = await quest_service.complete_quest_if_available(mocked_user, "Quest title")
        # Assert
        assert res == quest

    async def test_cannot_complete_nonexistent_quest(self, mocked_user, mock_container):
        # Arrange
        mock_quest_repository = AsyncMagicMock(get_first=CoroutineMock(return_value=None))
        quest_service = QuestService(repository=mock_quest_repository)
        # Act & Assert
        with pytest.raises(QuestDNE):
            await quest_service.complete_quest_if_available(mocked_user, "Quest Title")

    async def test_cannot_complete_unaccepted_quest(self, mocked_user, mock_container):
        # Arrange
        mock_quest_repository = AsyncMagicMock(
            get_first=CoroutineMock(return_value=MagicMock(users=[]), session=AsyncMagicMock(commit=CoroutineMock()))
        )
        quest_service = QuestService(repository=mock_quest_repository)
        # Act & Assert
        with pytest.raises(QuestNotAccepted):
            await quest_service.complete_quest_if_available(mocked_user, "Quest Title")

    async def test_max_completion_count_reached(self, mocked_user, mock_container):
        # Arrange
        quest = MagicMock(users=[mocked_user], max_completion_count=1, completed_users=[mocked_user])
        mock_quest_repository = AsyncMagicMock(
            get_first=CoroutineMock(return_value=quest, session=AsyncMagicMock(commit=CoroutineMock()))
        )
        quest_service = QuestService(repository=mock_quest_repository)
        # Act & Assert
        with pytest.raises(MaxQuestCompletionReached):
            await quest_service.complete_quest_if_available(mocked_user, "Quest title")
