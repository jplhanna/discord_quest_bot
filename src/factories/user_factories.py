from src.factories.base_factories import BaseFactory
from src.models import User


class UserFactory(BaseFactory[User]):
    __model__ = User
    __set_as_default_factory_for_type__ = True
