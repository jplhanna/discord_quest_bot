from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

from src.constants import DayOfWeek
from src.tavern import Menu
from src.tavern import TavernService
from src.tavern.exceptions import NoMenuItemFoundError
from src.tavern.models import MenuItem


class TestDeleteMenuItem:
    @pytest.mark.parametrize(
        ("menu_items", "item_name", "day_of_week"),
        [
            ([MenuItem(food="Food", day_of_the_week=DayOfWeek.MONDAY)], "Not food", DayOfWeek.MONDAY),
            ([MenuItem(food="Food", day_of_the_week=DayOfWeek.MONDAY)], "Not food", None),
            ([MenuItem(food="Food", day_of_the_week=DayOfWeek.MONDAY)], "Food", DayOfWeek.WEDNESDAY),
            ([], "Food", DayOfWeek.MONDAY),
            ([], "Food", None),
        ],
    )
    async def test_no_items_found(self, faker, menu_items, item_name, day_of_week):
        # Arrange
        tavern_service = TavernService(repository_factory=AsyncMock(), menu_item_model=MagicMock())
        menu = Menu(
            server_id=faker.random_number(digits=10, fix_len=True), start_date=faker.date_object(), items=menu_items
        )

        # Act & Assert
        with pytest.raises(NoMenuItemFoundError, match=f"No menu item could be found with the name {item_name}"):
            await tavern_service.delete_menu_item(menu, item_name, day_of_week)

    @pytest.mark.parametrize("day_of_week", [None, DayOfWeek.MONDAY])
    async def test_item_deleted(self, faker, day_of_week):
        # Arrange
        menu_item_repository = AsyncMock(delete=AsyncMock())
        mock_repository_factory = MagicMock(return_value=menu_item_repository)
        tavern_service = TavernService(repository_factory=mock_repository_factory, menu_item_model=MagicMock())
        menu_item = MenuItem(food="Food", day_of_the_week=DayOfWeek.MONDAY)
        menu = Menu(
            server_id=faker.random_number(digits=10, fix_len=True), start_date=faker.date_object(), items=[menu_item]
        )
        # Act
        await tavern_service.delete_menu_item(menu, "Food", day_of_week)
        # Assert
        menu_item_repository.delete.assert_called_with(menu_item)
