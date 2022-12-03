from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import MappedAsDataclass
from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.helpers.sqlalchemy_helpers import BaseModel
from src.helpers.sqlalchemy_helpers import many_to_many_table
from src.helpers.sqlalchemy_helpers import snake_case_table_name
from src.typeshed import MixinData


class CoreModelMixin(MappedAsDataclass, BaseModel):
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
    quests: Mapped[list["Quest"]] = relationship(
        "Quest", default_factory=list, repr=False, secondary="user_quest", back_populates="users"
    )
    experience: Mapped[list["ExperienceTransaction"]] = relationship(
        "ExperienceTransaction", back_populates="user", default_factory=list, repr=False
    )


class UserResourceMixin:
    __user_mixin_data__: MixinData

    @declared_attr
    def user_id(self) -> Mapped[int]:
        return mapped_column(ForeignKey("user.id"), init=False)

    @declared_attr
    def user(self) -> Mapped[User]:
        return relationship(User, back_populates=self.__user_mixin_data__.get("back_populates"))


class Quest(CoreModelMixin):
    """
    A representation of an event(quest) a user can take part in

    Attributes
    __________
    name: str
        Name of the quest
    experience: int
        How much experience a user will earn upon completion of a quest
    users: list[User]
        List of users who have accepted this quest
    """

    # Columns
    name: Mapped[str]
    experience: Mapped[int]

    # Relationships
    users: Mapped[list[User]] = relationship(
        "User", default_factory=list, secondary="user_quest", back_populates="quests"
    )


user_quest = many_to_many_table("User", "Quest")


class ExperienceTransaction(CoreModelMixin, UserResourceMixin):
    """
    Representation of an instance of a user earning experience

    Attributes
    __________
    user_id: int
        ID for user who earned this experience
    quest_id: int
        ID for quest that the user earned this experience from
    user: User
    quest: Quest
    """

    __user_mixin_data__ = MixinData(back_populates="experience")

    # Columns
    quest_id: Mapped[int] = mapped_column(ForeignKey("quest.id"), init=False)
    experience: Mapped[int] = mapped_column(init=False)

    # Relationship
    quest: Mapped[Quest] = relationship(Quest)

    def __post_init__(self) -> None:
        self.experience = self.quest.experience
