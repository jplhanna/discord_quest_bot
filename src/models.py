from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import MappedAsDataclass
from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from src.helpers.sqlalchemy_helpers import BaseModel
from src.helpers.sqlalchemy_helpers import snake_case_table_name
from src.typeshed import MixinData

if TYPE_CHECKING:
    from src.quests import ExperienceTransaction
    from src.quests import Quest


class CoreModelMixin(MappedAsDataclass, BaseModel, kw_only=True):
    @declared_attr  # type: ignore[arg-type]
    def __tablename__(self) -> str:  # pylint: disable=E0213
        return snake_case_table_name(self.__name__)

    __abstract__ = True
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    datetime_created: Mapped[datetime] = mapped_column(init=False, default_factory=datetime.utcnow, repr=False)
    datetime_edited: Mapped[datetime] = mapped_column(
        init=False, default_factory=datetime.utcnow, repr=False, onupdate=datetime.utcnow
    )


class User(CoreModelMixin):
    """
    Representation of a registered discord user

    ...
    Attributes
    __________
    discord_id: int
        The discord side id
    quests: list[Quest]
        List of quests that a user has accepted
    """

    # Columns
    discord_id: Mapped[int] = mapped_column(BigInteger, unique=True)

    # Relationships
    quests: Mapped[list["Quest"]] = relationship("UserQuest", default_factory=list, repr=False, back_populates="user")
    experience: Mapped[list["ExperienceTransaction"]] = relationship(
        "ExperienceTransaction", back_populates="user", default_factory=list, repr=False
    )


class UserResourceMixin(MappedAsDataclass):
    class Meta:
        user_mixin_data: MixinData = MixinData()

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), init=False, repr=False, index=Meta.user_mixin_data.get("index")
    )

    @declared_attr
    def user(self) -> Mapped[User]:
        return relationship(User, back_populates=self.Meta.user_mixin_data.get("back_populates"))
