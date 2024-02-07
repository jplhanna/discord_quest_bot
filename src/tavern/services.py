from datetime import datetime
from datetime import timedelta
from typing import cast

from sqlalchemy import Date
from sqlalchemy import cast as sql_cast
from sqlalchemy.orm import QueryableAttribute
from sqlalchemy.orm import selectinload
from sqlmodel import desc

from src.constants import DayOfWeek
from src.helpers.sqlalchemy_helpers import QueryArgs
from src.repositories import BaseRepository
from src.services import MultiRepoService
from src.tavern.exceptions import NoMenuItemFoundError
from src.tavern.models import Menu
from src.tavern.models import MenuItem
from src.typeshed import RepositoryHandler


class TavernRepositoryHandler(RepositoryHandler):
    menu: BaseRepository[Menu]
    menu_item: BaseRepository[MenuItem]


class TavernService(MultiRepoService):
    _repositories: TavernRepositoryHandler

    async def get_this_weeks_menu(self, server_id: int) -> Menu | None:
        today = datetime.today()
        return await self._repositories.menu.get_first(
            QueryArgs(
                filter_dict={"server_id": server_id},
                filter_list=[sql_cast(today, Date).between(Menu.start_date, Menu.start_date + timedelta(days=7))],
                eager_options=[selectinload(cast(QueryableAttribute, Menu.items))],
                order_by=[desc(Menu.start_date)],
            )
        )

    async def create_menu_for_week(self, server_id: int) -> Menu:
        menu = Menu(server_id=server_id)
        await self._repositories.menu.add(menu, and_refresh=["items"])
        return menu

    async def insert_menu_item(self, menu: Menu, item_name: str, day_of_week: DayOfWeek) -> None:
        menu_item = MenuItem(food=item_name, day_of_the_week=day_of_week)
        menu.items.append(menu_item)
        await self._repositories.menu.update()

    async def delete_menu_item(self, menu: Menu, item_name: str, day_of_week: DayOfWeek | None) -> None:
        items = menu.grouped_items[day_of_week] if day_of_week else menu.items

        for item in items:
            if item.food == item_name:
                await self._repositories.menu_item.delete(item)
        else:
            raise NoMenuItemFoundError(item_name)
