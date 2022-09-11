from datetime import datetime
from typing import List

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
    __repr_fields__: List[str] = []

    __abstract__ = True
    id = Column(Integer, primary_key=True)
    datetime_created = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        fields = ["id"] + self.__repr_fields__
        _repr = " ".join([f"{repr_field}: {getattr(self, repr_field)}" for repr_field in fields])
        return _repr


class User(CoreModelMixin):
    # Columns
    discord_id: int = Column(BigInteger, unique=True)

    # Relationships
    quests: list["Quest"] = relationship("Quest", secondary="user_quest", back_populates="users", uselist=True)


class Quest(CoreModelMixin):
    __repr_fields__ = ["name", "experience"]
    # Columns
    name: str = Column(String, nullable=False)
    experience: int = Column(Integer, nullable=False)

    # Relationships
    users: list[User] = relationship("User", secondary="user_quest", back_populates="quests", uselist=True)


user_quest = many_to_many_table("User", "Quest")
