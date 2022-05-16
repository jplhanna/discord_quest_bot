from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
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
    discord_id = Column(BigInteger, unique=True)


class Quest(CoreModelMixin):
    # Columns
    experience = Column(Integer, nullable=False)

    # Relationships
    user = relationship("User", secondary="user_quest", backref="quests")


user_quest = many_to_many_table("User", "Quest")
