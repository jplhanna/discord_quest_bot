from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import MappedAsDataclass
from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.helpers.sqlalchemy_helpers import BaseModel
from src.helpers.sqlalchemy_helpers import snake_case_table_name
from src.typeshed import MixinData


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


class UserResourceMixin:
    __user_mixin_data__: MixinData

    @declared_attr
    def user_id(self) -> Mapped[int]:
        return mapped_column(ForeignKey("user.id"), init=False, repr=False)

    @declared_attr
    def user(self) -> Mapped[User]:
        return relationship(User, back_populates=self.__user_mixin_data__.get("back_populates"))


class Quest(CoreModelMixin):
    """
    A representation of an event(quest) a user can take part in

    Attributes
    ----------
    name: str
        Name of the quest
    experience: int
        How much experience a user will earn upon completion of a quest
    users: list[User]
        List of users who have accepted this quest
    max_completion_count: Optional[int]
        Number of times a quest can be completed by a single user, if None can be completed an infinite number of times
    """

    # Columns
    name: Mapped[str]
    experience: Mapped[int]
    max_completion_count: Mapped[int | None] = mapped_column(default=None)

    # Relationships
    users: Mapped[list[User]] = relationship("UserQuest", default_factory=list, back_populates="quest", repr=False)


class UserQuest(CoreModelMixin, UserResourceMixin):
    __user_mixin_data__ = MixinData(back_populates="quests", index=True)

    # Columns
    quest_id: Mapped[int] = mapped_column(
        ForeignKey("quest.id", ondelete="CASCADE"), index=True, repr=False, init=False
    )
    date_completed: Mapped[datetime | None] = mapped_column(init=False, default=None)

    # Relationships
    quest: Mapped[Quest] = relationship(Quest, back_populates="users")

    @property
    def completed(self) -> bool:
        return self.date_completed is not None

    def mark_complete(self) -> None:
        self.date_completed = datetime.utcnow()

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, User):
            return self.user == other  # pylint: disable=W0143
        if isinstance(other, Quest):
            return self.quest == other
        if isinstance(other, UserQuest):
            return self.id == other.id
        raise TypeError(f"Cannot compare with {other}.")


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
