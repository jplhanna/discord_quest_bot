from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from polyfactory.factories.sqlalchemy_factory import T


class BaseFactory(SQLAlchemyFactory[T]):
    __is_base_factory__ = True
    __max_collection_length__ = 2
    __randomize_collection_length__ = True
    __use_defaults__ = True
