from datetime import date
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.models import CoreModelMixin


class Menu(CoreModelMixin):
    server_id: Mapped[int]
    start_date: Mapped[date] = mapped_column(default_factory=datetime.today)
    items: Mapped[list["MenuItem"]] = relationship("MenuItem", back_populates="menu", default_factory=list)


class MenuItem(CoreModelMixin):
    # Columns
    food: Mapped[str]
    day_of_the_week: Mapped[int]

    menu_id: Mapped[int] = mapped_column(ForeignKey("menu.id", ondelete="CASCADE"), init=False, repre=False)

    # relationships
    menu: Mapped[Menu] = relationship(Menu, back_populates="items")