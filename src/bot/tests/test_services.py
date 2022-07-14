from unittest.mock import MagicMock

from asynctest import CoroutineMock
from asynctest import MagicMock as AsyncMagicMock
from pytest import mark

from src.constants import GOOD_LUCK_ADVENTURER
from src.constants import QUEST_ALREADY_ACCEPTED
from src.constants import QUEST_DOES_NOT_EXIST
from src.services import QuestService


@mark.asyncio
class TestQuestService:
    @mark.parametrize(
        "quest, result",
        [(MagicMock(users=[]), GOOD_LUCK_ADVENTURER), (None, QUEST_DOES_NOT_EXIST)],
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

    async def test_quest_already_accepted(self, mocked_user, mock_container):
        # Arrange
        quest = MagicMock(users=[mocked_user])
        mock_quest_repository = AsyncMagicMock(
            get_first=CoroutineMock(return_value=quest), session=AsyncMagicMock(commit=CoroutineMock())
        )
        quest_service = QuestService(repository=mock_quest_repository)
        # Act
        res = await quest_service.accept_quest_if_available(mocked_user, "Quest title")
        # Assert
        assert res == QUEST_ALREADY_ACCEPTED
