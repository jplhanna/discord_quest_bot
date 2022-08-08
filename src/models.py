from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship

from src.helpers.sqlalchemy_helpers import BaseModel
from src.helpers.sqlalchemy_helpers import TableMeta
from src.helpers.sqlalchemy_helpers import many_to_many_table


class CoreModelMixin(BaseModel, metaclass=TableMeta):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    datetime_created = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"ID: {self.id}"


class User(CoreModelMixin):
    # Columns
    discord_id = Column(BigInteger, unique=True)

    # Relationships
    quests = relationship("Quest", secondary="user_quest", back_populates="users", uselist=True)


class Quest(CoreModelMixin):
    # Columns
    name = Column(String, nullable=False)
    experience = Column(Integer, nullable=False)

    # Relationships
    users = relationship("User", secondary="user_quest", back_populates="quests", uselist=True)


user_quest = many_to_many_table("User", "Quest")
