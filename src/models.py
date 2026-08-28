from datetime import datetime
from typing import TYPE_CHECKING
from typing import override

from pydantic import ConfigDict
from sqlalchemy import BigInteger
from sqlalchemy.orm import declared_attr
from sqlmodel import Field
from sqlmodel import Relationship

from helpers.sqlalchemy_helpers import BaseModel
from helpers.sqlalchemy_helpers import snake_case_table_name
from typeshed import MixinData
from typeshed import NonEmptyString

if TYPE_CHECKING:
    from quests import ExperienceTransaction
    from quests import UserQuest


class CoreModelMixin(BaseModel):
    __abstract__ = True
    model_config = ConfigDict(  # type: ignore[assignment]
        str_strip_whitespace=True, str_to_lower=True, from_attributes=True
    )

    @override
    @declared_attr  # type: ignore[arg-type]
    def __tablename__(self) -> str:
        return snake_case_table_name(self.__name__)

    id: int | None = Field(primary_key=True, default=None)
    datetime_created: datetime = Field(default_factory=lambda: datetime.now(), repr=False)
    datetime_edited: datetime = Field(
        default_factory=lambda: datetime.now(), repr=False, sa_column_kwargs={"onupdate": datetime.now}
    )


class User(CoreModelMixin, table=True):
    """
    Representation of a registered discord user.

    ...

    Attributes
    ----------
    discord_id: int
        The discord side id
    quests: list[Quest]
        List of quests that a user has accepted
    """

    # Columns
    discord_id: int = Field(sa_type=BigInteger, unique=True)

    # Relationships
    quests: list["UserQuest"] = Relationship(back_populates="user")
    experience: list["ExperienceTransaction"] = Relationship(back_populates="user")


class UserResourceMixin(BaseModel):
    class Meta:
        user_mixin_data: MixinData = MixinData()

    user_id: int = Field(foreign_key="user.id", repr=False, index=Meta.user_mixin_data.index)


class Theme(CoreModelMixin, table=True):
    name: NonEmptyString
