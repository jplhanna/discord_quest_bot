import factory

from pytest_factoryboy import register

from src.helpers.factories.base_factories import BaseFactory
from src.models import User


@register
class UserFactory(BaseFactory):
    id = factory.Sequence(lambda n: n + 1)

    class Meta:
        model = User

    discord_id = factory.Faker("random_number", digits=10)
