from unittest.mock import MagicMock
from unittest.mock import sentinel

from pytest import mark

from bot.constants import ALREADY_REGISTERED_MESSAGE
from bot.constants import NEW_USER_MESSAGE
from bot.controllers import check_and_register_user

wire_to = ["bot.controllers"]


class TestCheckAndRegisterUser:
    @mark.parametrize("user_exists, expected_result", [(True, ALREADY_REGISTERED_MESSAGE), (False, NEW_USER_MESSAGE)])
    def test_account_already_exists(self, mock_container, user_exists, expected_result):
        # Arrange
        ctx = MagicMock(author=MagicMock(id=sentinel.discord_id))
        mocked_user_service = MagicMock(get_user_by_discord_id=MagicMock(return_value=user_exists))
        mock_container.user_service.override(mocked_user_service)
        mock_container.wire(wire_to)
        # Act
        res = check_and_register_user(ctx)
        # Assert
        mocked_user_service.get_user_by_discord_id.assert_called_with(sentinel.discord_id)
        assert res == expected_result
