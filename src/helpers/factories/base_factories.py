from factory.alchemy import SQLAlchemyModelFactory
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from src.config import DBSettings

db_settings = DBSettings()

test_session = scoped_session(sessionmaker())


class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = test_session
