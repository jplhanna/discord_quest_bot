from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import sentinel

import pytest

from src.bot.constants import ALREADY_REGISTERED_MESSAGE
from src.bot.constants import NEW_USER_MESSAGE
from src.bot.constants import REGISTER_FIRST_MESSAGE
from src.bot.controllers import add_quest_to_user
from src.bot.controllers import check_and_register_user

wire_to = ["src.bot.controllers"]


@pytest.fixture(params=[True, False])
def mock_container_if_user_exists(mock_container, mocked_user, request):
    mocked_user_service = AsyncMock(
        get_user_by_discord_id=AsyncMock(return_value=mocked_user if request.param else None)
    )
    mock_container.user_service.override(mocked_user_service)
    mock_container.wire(wire_to)
    return mock_container, mocked_user_service, request.param


class TestCheckAndRegisterUser:
    @pytest.mark.asyncio()
    async def test_account_already_exists(self, mock_container_if_user_exists):
        # Arrange
        _, mocked_user_service, user_exists = mock_container_if_user_exists
        expected_result_mapping = {True: ALREADY_REGISTERED_MESSAGE, False: NEW_USER_MESSAGE}
        ctx = MagicMock(author=MagicMock(id=sentinel.discord_id))
        # Act
        res = await check_and_register_user(ctx)
        # Assert
        mocked_user_service.get_user_by_discord_id.assert_called_with(sentinel.discord_id)
        assert res == expected_result_mapping[user_exists]


@pytest.mark.asyncio()
class TestAddQuestToUser:
    async def test_if_registered(self, mock_container_if_user_exists):
        # Arrange
        mock_container, _, user_exists = mock_container_if_user_exists
        ctx = MagicMock(author=MagicMock(id=sentinel.discord_id))
        mocked_quest_service = AsyncMock()
        mock_container.quest_service.override(mocked_quest_service)
        mock_container.wire(wire_to)
        # Act
        res = await add_quest_to_user(ctx, sentinel.quest_name)
        # Assert
        assert (res == REGISTER_FIRST_MESSAGE) is not user_exists
        assert mocked_quest_service.accept_quest_if_available.called is user_exists
