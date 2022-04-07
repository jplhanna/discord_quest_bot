from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy.ext.declarative import declarative_base

BaseModel = declarative_base()


class CoreModelMixin(BaseModel):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    datetime_created = Column(DateTime, nullable=False, default=datetime.utcnow())


class User(CoreModelMixin):
    __tablename__ = 'user'
    discord_id = Column(Integer, unique=True)
