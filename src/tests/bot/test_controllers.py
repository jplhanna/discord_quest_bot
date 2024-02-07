from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import sentinel

import pytest

from src.bot.constants import ALREADY_REGISTERED_MESSAGE
from src.bot.constants import NEW_USER_MESSAGE
from src.bot.constants import NO_MENU_THIS_WEEK_MESSAGE
from src.bot.constants import REGISTER_FIRST_MESSAGE
from src.bot.constants import SERVER_ONLY_BAD_REQUEST_MESSAGE
from src.bot.controllers import add_quest_to_user
from src.bot.controllers import check_and_register_user
from src.bot.controllers import complete_quest_for_user
from src.bot.controllers import get_tavern_menu
from src.bot.controllers import upsert_tavern_menu
from src.constants import QUEST_DOES_NOT_EXIST
from src.constants import DayOfWeek
from src.quests.exceptions import QuestDNE
from src.tavern import Menu
from src.tavern.models import MenuItem

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


@pytest.mark.asyncio()
class TestCompleteQuestForUser:
    async def test_if_registered(self, mock_container_if_user_exists, mocked_ctx):
        # Arrange
        mock_container, _, user_exists = mock_container_if_user_exists
        mocked_quest_service = AsyncMock()
        mocked_xp_service = AsyncMock()
        mock_container.quest_service.override(mocked_quest_service)
        mock_container.xp_service.override(mocked_xp_service)
        mock_container.wire(wire_to)

        # Act
        res = await complete_quest_for_user(mocked_ctx, sentinel.quest_name)

        # Assert
        assert (res == REGISTER_FIRST_MESSAGE) is not user_exists
        assert mocked_quest_service.complete_quest_if_available.called is user_exists
        assert mocked_xp_service.earn_xp_for_quest.called is user_exists

    @pytest.mark.parametrize("mock_container_if_user_exists", [True], indirect=True)
    async def test_fails_to_complete(self, mock_container_if_user_exists, mocked_ctx):
        # Arrange
        mocked_quest_service = AsyncMock(
            complete_quest_if_available=AsyncMock(side_effect=QuestDNE(sentinel.quest_name))
        )
        mock_container, _, _ = mock_container_if_user_exists
        mock_container.quest_service.override(mocked_quest_service)
        mock_container.wire(wire_to)

        # Act
        res = await complete_quest_for_user(mocked_ctx, sentinel.quest_name)

        # Assert
        assert res == QUEST_DOES_NOT_EXIST


class TestGetTavernMenu:
    @pytest.mark.usefixtures("mock_container")
    async def test_get_no_guild(self, mocked_ctx):
        # Arrange
        mocked_ctx.guild = None
        # Act
        res = await get_tavern_menu(mocked_ctx)
        # Assert
        assert res == SERVER_ONLY_BAD_REQUEST_MESSAGE

    async def test_get_with_no_menu(self, mocked_ctx, mock_container):
        # Arrange
        menu_service = AsyncMock(get_this_weeks_menu=AsyncMock(return_value=None))
        mock_container.tavern_service.override(menu_service)
        mock_container.wire(wire_to)

        # Act
        res = await get_tavern_menu(mocked_ctx)

        # Assert
        assert res == NO_MENU_THIS_WEEK_MESSAGE

    async def test_get_tavern_menu(self, mock_container, mocked_ctx):
        # Arrange
        menu_item = MenuItem(food="test", day_of_the_week=DayOfWeek.MONDAY)
        menu_service = AsyncMock(
            get_this_weeks_menu=AsyncMock(
                return_value=Menu(server_id=sentinel.guild_id, start_date=sentinel.menu_start_date, items=[menu_item])
            )
        )
        mock_container.tavern_service.override(menu_service)
        mock_container.wire(wire_to)
        # Act
        res = await get_tavern_menu(mocked_ctx)
        # Assert
        assert res == (
            "Menu\n"
            "**Sunday**:\n"
            "  No items available.\n"
            "**Monday**:\n"
            f"  - {menu_item.food}\n"
            "**Tuesday**:\n"
            "  No items available.\n"
            "**Wednesday**:\n"
            "  No items available.\n"
            "**Thursday**:\n"
            "  No items available.\n"
            "**Friday**:\n"
            "  No items available.\n"
            "**Saturday**:\n"
            "  No items available."
        )


class TestUpsertTavernMenu:
    @pytest.mark.usefixtures("mock_container")
    async def test_no_guild(self, mocked_ctx):
        # Arrange
        mocked_ctx.guild = None
        # Act
        res = await upsert_tavern_menu(mocked_ctx, "fake", DayOfWeek.MONDAY)
        # Assert
        assert res == SERVER_ONLY_BAD_REQUEST_MESSAGE

    async def test_no_pre_existing_menu(self, mocked_ctx, mock_container):
        # Arrange
        tavern_service = AsyncMock(get_this_weeks_menu=AsyncMock(return_value=None))
        mock_container.tavern_service.override(tavern_service)
        mock_container.wire(wire_to)
        # Act
        res = await upsert_tavern_menu(mocked_ctx, "New item", DayOfWeek.MONDAY)
        # Assert
        assert res == "Item added"
        tavern_service.create_menu_for_week.assert_called_with(mocked_ctx.guild.id)
        menu = tavern_service.create_menu_for_week.return_value
        tavern_service.insert_menu_item.assert_called_with(menu, "New item", DayOfWeek.MONDAY)

    async def test_with_pre_existing_menu(self, mocked_ctx, mock_container, faker):
        # Arrange
        menu = Menu(start_date=faker.date(), server_id=mocked_ctx.guild.id)
        tavern_service = AsyncMock(get_this_weeks_menu=AsyncMock(return_value=menu))
        mock_container.tavern_service.override(tavern_service)
        mock_container.wire(wire_to)
        # Act
        res = await upsert_tavern_menu(mocked_ctx, "New item", DayOfWeek.MONDAY)
        # Assert
        assert res == "Item added"
        tavern_service.create_menu_for_week.assert_not_called()
        tavern_service.insert_menu_item.assert_called_with(menu, "New item", DayOfWeek.MONDAY)
