from datetime import datetime

from sqlmodel import Field
from sqlmodel import Relationship

from src.models import CoreModelMixin
from src.models import User
from src.models import UserResourceMixin
from src.typeshed import MixinData
from src.typeshed import NonEmptyString


class Quest(CoreModelMixin, table=True):
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
    name: NonEmptyString
    experience: int
    max_completion_count: int | None = Field(default=None)

    # Relationships
    users: list[User] = Relationship(sa_relationship_args=["user_quest"], back_populates="quests")


class UserQuest(CoreModelMixin, UserResourceMixin, table=True):
    class Meta:
        user_mixin_data = MixinData(back_populates="quests", index=True)

    # Columns
    quest_id: int = Field(foreign_key="quest.id", index=True, repr=False)
    date_completed: datetime | None = Field(default=None)

    # Relationships
    quest: Quest = Relationship()
    user: User = Relationship()

    @property
    def completed(self) -> bool:
        return self.date_completed is not None

    def mark_complete(self) -> None:
        self.date_completed = datetime.utcnow()


class ExperienceTransaction(CoreModelMixin, UserResourceMixin, table=True):
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
    quest_id: int = Field(foreign_key="quest.id", repr=False)
    experience: int = Field()

    # Relationship
    quest: Quest = Relationship()
    user: User = Relationship(back_populates="experience")

    def __post_init__(self) -> None:
        self.experience = self.quest.experience
