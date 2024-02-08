from datetime import date

import pytest

from src.constants import DayOfWeek
from src.tavern import Menu
from src.tavern.models import MenuItem


class TestMenu:
    @pytest.mark.parametrize(
        ("items", "update_dict"),
        [
            ([item1 := MenuItem(food="food", day_of_the_week=DayOfWeek.SATURDAY)], {DayOfWeek.SATURDAY: [item1]}),
            ([], {}),
            (
                [
                    item1 := MenuItem(food="food", day_of_the_week=DayOfWeek.MONDAY),
                    item2 := MenuItem(food="food 2", day_of_the_week=DayOfWeek.WEDNESDAY),
                    item3 := MenuItem(food="food", day_of_the_week=DayOfWeek.MONDAY),
                ],
                {DayOfWeek.MONDAY: [item1, item3], DayOfWeek.WEDNESDAY: [item2]},
            ),
        ],
    )
    def test_grouped_items(self, items, update_dict):
        # Arrange
        menu = Menu(server_id=1, start_date=date(2020, 1, 1), items=items)
        # Act
        res = menu.grouped_items
        # Assert
        test_res = {
            DayOfWeek.SUNDAY: [],
            DayOfWeek.MONDAY: [],
            DayOfWeek.TUESDAY: [],
            DayOfWeek.WEDNESDAY: [],
            DayOfWeek.THURSDAY: [],
            DayOfWeek.FRIDAY: [],
            DayOfWeek.SATURDAY: [],
        }
        test_res.update(update_dict)
        assert res == test_res
