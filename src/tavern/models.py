from datetime import date
from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlmodel import Field
from sqlmodel import Relationship

from src.constants import DayOfWeek
from src.helpers.sqlalchemy_helpers import EnumColumn
from src.models import CoreModelMixin
from src.models import Theme


class Menu(CoreModelMixin, table=True):
    server_id: int = Field(sa_type=BigInteger)
    start_date: date = Field(default_factory=datetime.today)
    items: list["MenuItem"] = Relationship(back_populates="menu")

    @property
    def grouped_items(self) -> dict[DayOfWeek, list["MenuItem"]]:
        dow_items: dict[DayOfWeek, list[MenuItem]] = {day: [] for day in DayOfWeek}
        for item in self.items:
            dow_items[item.day_of_the_week].append(item)
        return dow_items


class MenuItem(CoreModelMixin, table=True):
    # Columns
    food: str
    day_of_the_week: DayOfWeek = Field(sa_column=Column(EnumColumn(DayOfWeek)))

    menu_id: int = Field(foreign_key="menu.id", repr=False)

    # relationships
    menu: Menu = Relationship(back_populates="items")


class BardTale(CoreModelMixin, table=True):
    story: str

    theme_id: int = Field(foreign_key="theme.id", repr=False)

    theme: Theme
