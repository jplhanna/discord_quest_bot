from unittest.mock import AsyncMock

import pytest

from src.constants import DayOfWeek
from src.tavern import Menu
from src.tavern import TavernService
from src.tavern.exceptions import NoMenuItemFoundError
from src.tavern.models import MenuItem


class TestDeleteMenuItem:
    @pytest.mark.parametrize(
        ("item_name", "day_of_week"),
        [("Not food", DayOfWeek.MONDAY), ("Not food", None), ("Food", DayOfWeek.WEDNESDAY)],
    )
    async def test_no_items_found(self, faker, item_name, day_of_week):
        # Arrange
        menu_item_repo = AsyncMock()
        tavern_service = TavernService(menu_item_repository=menu_item_repo)
        menu_item = MenuItem(food="Food", day_of_the_week=DayOfWeek.MONDAY)
        menu = Menu(
            server_id=faker.random_number(digits=10, fix_len=True), start_date=faker.date_object(), items=[menu_item]
        )

        # Act & Assert
        with pytest.raises(NoMenuItemFoundError, match=f"No menu item could be found with the name {item_name}"):
            await tavern_service.delete_menu_item(menu, item_name, day_of_week)
