from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from polyfactory.factories.sqlalchemy_factory import T


class BaseFactory(SQLAlchemyFactory[T]):
    __is_base_factory__ = True
    __min_collection_length__ = 1
    __max_collection_length__ = 2
    __randomize_collection_length__ = True
    __use_defaults__ = True
    __allow_none_optionals__ = False
