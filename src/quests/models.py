from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.models import CoreModelMixin
from src.models import User
from src.models import UserResourceMixin
from src.typeshed import MixinData
from src.typeshed import SQLLogicType


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
    class Meta:
        user_mixin_data = MixinData(back_populates="quests", index=True)

    # Columns
    quest_id: Mapped[int] = mapped_column(
        ForeignKey("quest.id", ondelete="CASCADE"), index=True, repr=False, init=False
    )
    date_completed: Mapped[datetime | None] = mapped_column(init=False, default=None)

    # Relationships
    quest: Mapped[Quest] = relationship(Quest, back_populates="users")

    @hybrid_property
    def completed(self) -> bool:
        return self.date_completed is not None

    @completed.expression  # type: ignore[no-redef]
    def completed(self) -> SQLLogicType:
        return self.date_completed.isnot(None)

    def mark_complete(self) -> None:
        self.date_completed = datetime.utcnow()


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
    quest_id: Mapped[int] = mapped_column(ForeignKey("quest.id"), init=False, repr=False)
    experience: Mapped[int] = mapped_column(init=False)

    # Relationship
    quest: Mapped[Quest] = relationship(Quest)

    def __post_init__(self) -> None:
        self.experience = self.quest.experience
