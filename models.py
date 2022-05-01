from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy.ext.declarative import declarative_base

BaseModel = declarative_base()


class CoreModelMixin(BaseModel):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    datetime_created = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"ID: {self.id}"


class User(CoreModelMixin):
    __tablename__ = "user"
    discord_id = Column(BigInteger, unique=True)
