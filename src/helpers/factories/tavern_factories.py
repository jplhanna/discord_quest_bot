from unittest.mock import sentinel

import factory

from pytest_factoryboy import register

from src.constants import DayOfWeek
from src.helpers.factories.base_factories import BaseFactory
from src.tavern import Menu
from src.tavern.models import MenuItem


@register
class MenuItemFactory(BaseFactory):
    class Meta:
        model = MenuItem

    food = factory.Sequence(lambda n: f"Test Food {n}")
    day_of_the_week = factory.Iterator(DayOfWeek)
    menu = None


@register
class MenuFactory(BaseFactory):
    class Meta:
        model = Menu

    server_id = sentinel.guild_id
    start_date = factory.Faker("date_object")
    items = factory.RelatedFactoryList(MenuItemFactory, factory_related_name="menu")
