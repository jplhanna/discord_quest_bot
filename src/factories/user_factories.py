import factory

from pytest_factoryboy import register

from src.factories.base_factories import BaseFactory
from src.factories.base_factories import BasePolyFactory
from src.models import User


@register
class UserFactory(BaseFactory):
    id = factory.Sequence(lambda n: n + 1)

    class Meta:
        model = User

    discord_id = factory.Faker("random_number", digits=10)


class UserPolyFactory(BasePolyFactory[User]):
    __model__ = User
    __set_as_default_factory_for_type__ = True
