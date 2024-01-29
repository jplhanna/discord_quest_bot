from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from typing import cast

from sqlalchemy import func
from sqlalchemy.orm import QueryableAttribute
from sqlalchemy.orm import selectinload
from sqlmodel import desc

from src.helpers.sqlalchemy_helpers import QueryArgs
from src.repositories import BaseRepository
from src.services import BaseService
from src.tavern.models import Menu


@dataclass(frozen=True)
class MenuService(BaseService):
    _repository: BaseRepository[Menu]

    async def get_this_weeks_menu(self, server_id: int) -> Menu | None:
        today = datetime.today()
        return await self._repository.get_first(
            QueryArgs(
                filter_dict={"server_id": server_id},
                filter_list=[func.between(today, Menu.start_date, Menu.start_date + timedelta(days=7))],
                eager_options=[selectinload(cast(QueryableAttribute, Menu.items))],
                order_by_list=[desc(Menu.start_date)],
            )
        )

    async def upsert_menu_item(self, menu: Menu, item_name: str, day_of_the_week: int) -> None:
        pass
