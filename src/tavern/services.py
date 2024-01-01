from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta

from sqlalchemy import func
from sqlalchemy.orm import contains_eager

from src.helpers.sqlalchemy_helpers import QueryArgs
from src.repositories import BaseRepository
from src.services import BaseService
from src.tavern.models import Menu
from src.tavern.models import MenuItem


@dataclass(frozen=True)
class MenuService(BaseService):
    _repository: BaseRepository[Menu]

    async def get_this_weeks_menu(self, server_id: int) -> Menu | None:
        today = datetime.today()
        return await self._repository.get_first(
            QueryArgs(
                filter_dict={"server_id": server_id},
                filter_list=[func.between(today, Menu.start_date, Menu.start_date + timedelta(days=7))],
                eager_options=[contains_eager(Menu.items)],
                join_list=[Menu.items],
                order_by_list=[Menu.start_date, MenuItem.day_of_the_week],
            )
        )

    async def upsert_menu_item(self, menu: Menu, item_name: str, day_of_the_week: int) -> None:
        pass
