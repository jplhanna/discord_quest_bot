from unittest.mock import MagicMock

from asynctest import CoroutineMock
from asynctest import MagicMock as AsyncMagicMock
from pytest import mark

from src.services import QuestService


@mark.asyncio
class TestQuestService:
    @mark.parametrize(
        "quest, result",
        [(MagicMock(users=[]), "You have accepted {}! Good luck adventurer"), (None, "This quest does not exist")],
    )
    async def test_accept_quest_if_available(self, mocked_user, mock_container, quest, result):
        # Arrange
        mock_quest_repository = AsyncMagicMock(
            get_first=CoroutineMock(return_value=quest), session=AsyncMagicMock(commit=CoroutineMock())
        )
        quest_service = QuestService(repository=mock_quest_repository)
        # Act
        res = await quest_service.accept_quest_if_available(mocked_user, "Quest title")
        # Assert
        assert res == result.format("Quest title")
