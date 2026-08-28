from datetime import date
from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlmodel import Field
from sqlmodel import Relationship

from constants import DayOfWeek
from helpers.sqlalchemy_helpers import EnumColumn
from models import CoreModelMixin
from models import Theme
from typeshed import NonEmptyString


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
    food: NonEmptyString
    day_of_the_week: DayOfWeek = Field(sa_column=Column(EnumColumn(DayOfWeek)))

    menu_id: int = Field(foreign_key="menu.id", repr=False)

    # relationships
    menu: Menu = Relationship(back_populates="items")


class BardTale(CoreModelMixin, table=True):
    name: NonEmptyString
    story: NonEmptyString

    theme_id: int = Field(foreign_key="theme.id", repr=False)

    theme: Theme = Relationship()
