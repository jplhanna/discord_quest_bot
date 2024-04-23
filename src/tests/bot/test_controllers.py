from datetime import date
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import sentinel

import pytest

from src.bot.constants import ALREADY_REGISTERED_MESSAGE
from src.bot.constants import NEW_USER_MESSAGE
from src.bot.constants import NO_MENU_ITEMS_FOR_CHOSEN_DAY_MESSAGE
from src.bot.constants import NO_MENU_THIS_WEEK_MESSAGE
from src.bot.constants import REGISTER_FIRST_MESSAGE
from src.bot.constants import SERVER_ONLY_BAD_REQUEST_MESSAGE
from src.bot.controllers import add_quest_to_user
from src.bot.controllers import check_and_register_user
from src.bot.controllers import complete_quest_for_user
from src.bot.controllers import get_tavern_menu
from src.bot.controllers import remove_from_tavern_menu
from src.bot.controllers import select_from_tavern_menu
from src.bot.controllers import upsert_tavern_menu
from src.constants import QUEST_DOES_NOT_EXIST
from src.constants import ChooseStyle
from src.constants import DayOfWeek
from src.quests.exceptions import QuestDNE
from src.tavern import Menu
from src.tavern.exceptions import NoMenuItemFoundError
from src.tavern.models import MenuItem

wire_to = ["src.bot.controllers"]


@pytest.fixture(params=[True, False])
def mock_container_if_user_exists(mock_container, user, request):
    mocked_user_service = AsyncMock(get_user_by_discord_id=AsyncMock(return_value=user if request.param else None))
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
        tavern_service = AsyncMock(get_this_weeks_menu=AsyncMock(return_value=None))
        mock_container.tavern_service.override(tavern_service)
        mock_container.wire(wire_to)

        # Act
        res = await get_tavern_menu(mocked_ctx)

        # Assert
        assert res == NO_MENU_THIS_WEEK_MESSAGE

    async def test_get_tavern_menu(self, mock_container, mocked_ctx):
        # Arrange
        menu_item = MenuItem(food="test", day_of_the_week=DayOfWeek.MONDAY)
        tavern_service = AsyncMock(
            get_this_weeks_menu=AsyncMock(
                return_value=Menu(server_id=sentinel.guild_id, start_date=date(2024, 6, 6), items=[menu_item])
            )
        )
        mock_container.tavern_service.override(tavern_service)
        mock_container.wire(wire_to)
        # Act
        res = await get_tavern_menu(mocked_ctx)
        # Assert
        assert res == (
            "Menu for the week of Jun 06, 2024\n"
            "**Sunday**:\n"
            "  No items available.\n"
            "**Monday**:\n"
            f"  - {menu_item.food.capitalize()}\n"
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

    async def test_with_pre_existing_menu(self, mocked_ctx, mock_container, menu):
        # Arrange
        tavern_service = AsyncMock(get_this_weeks_menu=AsyncMock(return_value=menu))
        mock_container.tavern_service.override(tavern_service)
        mock_container.wire(wire_to)
        # Act
        res = await upsert_tavern_menu(mocked_ctx, "New item", DayOfWeek.MONDAY)
        # Assert
        assert res == "Item added"
        tavern_service.create_menu_for_week.assert_not_called()
        tavern_service.insert_menu_item.assert_called_with(menu, "New item", DayOfWeek.MONDAY)


class TestRemoveTavernMenu:
    @pytest.mark.usefixtures("mock_container")
    async def test_no_guild(self, mocked_ctx):
        # Arrange
        mocked_ctx.guild = None
        # Act
        res = await remove_from_tavern_menu(mocked_ctx, "fake", DayOfWeek.MONDAY)
        # Assert
        assert res == SERVER_ONLY_BAD_REQUEST_MESSAGE

    async def test_no_pre_existing_menu(self, mocked_ctx, mock_container):
        # Arrange
        tavern_service = AsyncMock(get_this_weeks_menu=AsyncMock(return_value=None))
        mock_container.tavern_service.override(tavern_service)
        mock_container.wire(wire_to)
        # Act
        res = await remove_from_tavern_menu(mocked_ctx, "New item", DayOfWeek.MONDAY)
        # Assert
        assert res == NO_MENU_THIS_WEEK_MESSAGE
        tavern_service.delete_menu_item.assert_not_called()

    @pytest.mark.parametrize(
        ("day_of_week", "error_text"),
        [
            (None, "Not food could not be found in this week's menu."),
            (DayOfWeek.MONDAY, "Not food could not be found on monday in this week's menu."),
        ],
    )
    async def test_item_not_found(self, mocked_ctx, mock_container, faker, day_of_week, error_text):
        # Arrange
        menu_item = MenuItem(food="Food", day_of_the_week=DayOfWeek.MONDAY)
        menu = Menu(start_date=faker.date_object(), server_id=mocked_ctx.guild.id, items=[menu_item])
        tavern_service = AsyncMock(
            get_this_weeks_menu=AsyncMock(return_value=menu),
            delete_menu_item=AsyncMock(side_effect=NoMenuItemFoundError("Not food")),
        )
        mock_container.tavern_service.override(tavern_service)
        mock_container.wire(wire_to)
        # Act
        res = await remove_from_tavern_menu(mocked_ctx, "Not food", day_of_week)
        # Assert
        assert res == error_text


class TestSelectFromTavernMenu:
    async def test_no_menu(self, mocked_guild, mock_container):
        # Arrange
        tavern_service = AsyncMock(get_this_weeks_menu=AsyncMock(return_value=None))
        mock_container.tavern_service.override(tavern_service)
        mock_container.wire(wire_to)
        # Act
        res = await select_from_tavern_menu(mocked_guild, ChooseStyle.RANDOM, DayOfWeek.MONDAY)
        # Assert
        assert res == NO_MENU_THIS_WEEK_MESSAGE

    async def test_no_items_for_selected_day(self, mocked_guild, mock_container, faker):
        # Arrange
        menu = Menu(start_date=faker.date_object(), server_id=mocked_guild.id)
        tavern_service = AsyncMock(get_this_weeks_menu=AsyncMock(return_value=menu))
        mock_container.tavern_service.override(tavern_service)
        mock_container.wire(wire_to)
        # Act
        res = await select_from_tavern_menu(mocked_guild, ChooseStyle.RANDOM, DayOfWeek.MONDAY)
        # Assert
        assert res == NO_MENU_ITEMS_FOR_CHOSEN_DAY_MESSAGE

    async def test_select_first(self, mocked_guild, mock_container, faker):
        # Arrange
        menu_item_1 = MenuItem(food="First food", day_of_the_week=DayOfWeek.MONDAY)
        menu_item_2 = MenuItem(food="Second food", day_of_the_week=DayOfWeek.MONDAY)
        menu = Menu(start_date=faker.date_object(), server_id=mocked_guild.id, items=[menu_item_1, menu_item_2])
        tavern_service = AsyncMock(get_this_weeks_menu=AsyncMock(return_value=menu))
        mock_container.tavern_service.override(tavern_service)
        mock_container.wire(wire_to)
        # Act
        res = await select_from_tavern_menu(mocked_guild, ChooseStyle.FIRST, DayOfWeek.MONDAY)
        # Assert
        assert res == f"Order Up!\n{menu_item_1.food.title()}"

    async def test_select_random(self, mocked_guild, mock_container, faker, mocker):
        # Arrange
        random_choice = mocker.patch("src.bot.controllers.random.choice")
        menu_item_1 = MenuItem(food="First food", day_of_the_week=DayOfWeek.MONDAY)
        menu_item_2 = MenuItem(food="Second food", day_of_the_week=DayOfWeek.MONDAY)
        menu = Menu(start_date=faker.date_object(), server_id=mocked_guild.id, items=[menu_item_1, menu_item_2])
        random_choice.return_value = menu_item_2
        tavern_service = AsyncMock(get_this_weeks_menu=AsyncMock(return_value=menu))
        mock_container.tavern_service.override(tavern_service)
        mock_container.wire(wire_to)
        # Act
        res = await select_from_tavern_menu(mocked_guild, ChooseStyle.RANDOM, DayOfWeek.MONDAY)
        # Assert
        assert res == f"Order Up!\n{menu_item_2.food.title()}"
        random_choice.assert_called_with([menu_item_1, menu_item_2])
