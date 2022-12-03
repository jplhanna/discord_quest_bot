from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import MappedAsDataclass
from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.helpers.sqlalchemy_helpers import BaseModel
from src.helpers.sqlalchemy_helpers import many_to_many_table
from src.helpers.sqlalchemy_helpers import snake_case_table_name


class CoreModelMixin(MappedAsDataclass, BaseModel):
    @declared_attr  # type: ignore[arg-type]
    def __tablename__(cls) -> str:  # pylint: disable=E0213
        return snake_case_table_name(cls.__name__)

    __abstract__ = True
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    datetime_created: Mapped[datetime] = mapped_column(init=False, default_factory=datetime.utcnow, repr=False)
    datetime_edited: Mapped[datetime] = mapped_column(
        init=False, default_factory=datetime.utcnow, repr=False, onupdate=datetime.utcnow
    )


class User(CoreModelMixin):
    # Columns
    discord_id: Mapped[int] = mapped_column(BigInteger, unique=True)

    # Relationships
    quests: Mapped[list["Quest"]] = relationship(
        "Quest", default_factory=list, repr=False, secondary="user_quest", back_populates="users"
    )


class Quest(CoreModelMixin):
    # Columns
    name: Mapped[str]
    experience: Mapped[int]

    # Relationships
    users: Mapped[list[User]] = relationship(
        "User", default_factory=list, secondary="user_quest", back_populates="quests"
    )


user_quest = many_to_many_table("User", "Quest")
