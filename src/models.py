from datetime import UTC
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import UUID4
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import SecretStr
from sqlalchemy import BigInteger
from sqlalchemy.orm import declared_attr
from sqlmodel import Field
from sqlmodel import Relationship

from src.helpers.sqlalchemy_helpers import BaseModel
from src.helpers.sqlalchemy_helpers import snake_case_table_name
from src.typeshed import MixinData
from src.typeshed import NonEmptyString

if TYPE_CHECKING:
    from src.quests import ExperienceTransaction
    from src.quests import Quest


class CoreModelMixin(BaseModel):
    __abstract__ = True
    model_config = ConfigDict(str_strip_whitespace=True, str_to_lower=True)  # type: ignore[assignment]

    @declared_attr  # type: ignore[override, arg-type]
    def __tablename__(self) -> str:
        return snake_case_table_name(self.__name__)

    id: int | None = Field(primary_key=True, default=None)
    datetime_created: datetime = Field(default_factory=lambda: datetime.now(UTC), repr=False)
    datetime_edited: datetime = Field(
        default_factory=lambda: datetime.now(UTC), repr=False, sa_column_kwargs={"onupdate": datetime.utcnow}
    )


class User(CoreModelMixin, table=True):
    """
    Representation of a registered discord user.

    ...

    Attributes
    ----------
    server_uuid: UUID
        The unique ID for litestar user management.
    discord_id: int
        The discord side id.
    quests: list[Quest]
        List of quests that a user has accepted.
    """

    # Columns
    discord_id: int | None = Field(sa_type=BigInteger, unique=True)
    server_uuid: UUID4 = Field(default_factory=UUID4)
    email: EmailStr | None = Field(unique=True)
    username: NonEmptyString | None = Field(unique=True)
    password: SecretStr | None = Field(default=None)

    # Relationships
    quests: list["Quest"] = Relationship(sa_relationship_args=["user_quest"], back_populates="users")
    experience: list["ExperienceTransaction"] = Relationship(back_populates="user")


class UserResourceMixin(BaseModel):
    class Meta:
        user_mixin_data: MixinData = MixinData()

    user_id: int = Field(foreign_key="user.id", repr=False, index=Meta.user_mixin_data.index)


class Theme(CoreModelMixin, table=True):
    name: NonEmptyString
