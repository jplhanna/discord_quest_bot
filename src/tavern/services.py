from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from typing import cast

from sqlalchemy import Date
from sqlalchemy import cast as sql_cast
from sqlalchemy.orm import QueryableAttribute
from sqlalchemy.orm import selectinload
from sqlmodel import desc

from src.helpers.sqlalchemy_helpers import QueryArgs
from src.repositories import BaseRepository
from src.services import BaseService
from src.tavern.models import Menu
from src.tavern.models import MenuItem


@dataclass(frozen=True)
class TavernService(BaseService):
    _repository: BaseRepository[Menu]

    async def get_this_weeks_menu(self, server_id: int) -> Menu | None:
        today = datetime.today()
        return await self._repository.get_first(
            QueryArgs(
                filter_dict={"server_id": server_id},
                filter_list=[sql_cast(today, Date).between(Menu.start_date, Menu.start_date + timedelta(days=7))],
                eager_options=[selectinload(cast(QueryableAttribute, Menu.items))],
                order_by_list=[desc(Menu.start_date)],
            )
        )

    async def create_menu_for_week(self, server_id: int) -> Menu:
        menu = Menu(server_id=server_id)
        await self._repository.add(menu, and_refresh=["items"])
        return menu

    async def insert_menu_item(self, menu: Menu, item_name: str, day_of_the_week: int) -> None:
        menu_item = MenuItem(food=item_name, day_of_the_week=day_of_the_week)
        menu.items.append(menu_item)
        await self._repository.update()
