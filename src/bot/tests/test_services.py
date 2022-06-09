from unittest.mock import sentinel

from asynctest import CoroutineMock
from asynctest import MagicMock as AsyncMagicMock
from pytest import mark

from src.services import QuestService


@mark.asyncio
class TestQuestService:
    @mark.parametrize(
        "quest_exists, result",
        [(True, "You have accepted {}! Good luck adventurer"), (False, "This quest does not exist")],
    )
    async def test_accept_quest_if_available(self, mocked_user, mock_container, quest_exists, result):
        # Arrange
        session_factory = AsyncMagicMock()
        session_factory.return_value.__aenter__.return_value.commit = CoroutineMock()
        mock_quest_repository = AsyncMagicMock(
            get_first=CoroutineMock(return_value=quest_exists), session_factory=session_factory
        )
        quest_service = QuestService(repository=mock_quest_repository)
        # Act
        res = await quest_service.accept_quest_if_available(mocked_user, sentinel.quest_name)
        # Assert
        assert res == result.format(sentinel.quest_name)
