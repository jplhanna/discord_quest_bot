from dataclasses import dataclass
from dataclasses import field
from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship

from src.helpers.sqlalchemy_helpers import TableMeta
from src.helpers.sqlalchemy_helpers import many_to_many_table
from src.helpers.sqlalchemy_helpers import mapper_registry


@mapper_registry.mapped
@dataclass
class CoreModelMixin(metaclass=TableMeta):
    __abstract__ = True
    id: int = field(init=False, metadata={"sa": Column(Integer, primary_key=True)})  # pylint: disable=C0103
    datetime_created: datetime = field(
        init=False, default_factory=datetime.utcnow, repr=False, metadata={"sa": Column(DateTime, nullable=False)}
    )
    datetime_edited: datetime = field(
        init=False,
        default_factory=datetime.utcnow,
        repr=False,
        metadata={"sa": Column(DateTime, nullable=False, onupdate=datetime.utcnow)},
    )


@mapper_registry.mapped
@dataclass
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
    discord_id: int = field(metadata={"sa": Column(BigInteger, unique=True)})

    # Relationships
    quests: list["Quest"] = field(
        default_factory=list,
        repr=False,
        metadata={"sa": relationship("Quest", secondary="user_quest", back_populates="users")},
    )
    experience: list["ExperienceTransaction"] = field(
        default_factory=list, repr=False, metadata={"sa": relationship("ExperienceTransaction", back_populates="user")}
    )


@mapper_registry.mapped
@dataclass
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
    name: str = field(metadata={"sa": Column(String, nullable=False)})
    experience: int = field(metadata={"sa": Column(Integer, nullable=False)})

    # Relationships
    users: list[User] = field(
        default_factory=list, metadata={"sa": relationship(User, secondary="user_quest", back_populates="quests")}
    )


user_quest = many_to_many_table("User", "Quest")


@mapper_registry.mapped
@dataclass
class ExperienceTransaction(CoreModelMixin):
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

    # Columns
    user_id: int = field(init=False, metadata={"sa": Column(ForeignKey("user.id"), nullable=False)})
    quest_id: int = field(init=False, metadata={"sa": Column(ForeignKey("quest.id"), nullable=False)})

    # Relationship
    user: User = field(metadata={"sa": relationship(User, back_populates="experience")})
    quest: User = field(metadata={"sa": relationship(Quest)})
