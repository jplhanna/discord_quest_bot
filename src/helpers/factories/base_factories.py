from unittest.mock import MagicMock

from factory.alchemy import SQLAlchemyModelFactory


class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        # Due to using a different fixture to handle the async sessions,
        # we don't actually want to insert models when creating especially via the pytest-factory-boy fixtures
        sqlalchemy_session = MagicMock()
