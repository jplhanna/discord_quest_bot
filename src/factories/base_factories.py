from unittest.mock import MagicMock

from factory.alchemy import SQLAlchemyModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from polyfactory.factories.sqlalchemy_factory import T


class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        # Due to using a different fixture to handle the async sessions,
        # we don't actually want to insert models when creating especially via the pytest-factory-boy fixtures
        sqlalchemy_session = MagicMock()


class BasePolyFactory(SQLAlchemyFactory[T]):
    __is_base_factory__ = True
    __max_collection_length__ = 2
    __randomize_collection_length__ = True
    __use_defaults__ = True
