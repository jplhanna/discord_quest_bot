from datetime import date
from unittest.mock import sentinel

import factory

from polyfactory.decorators import post_generated
from pytest_factoryboy import register

from src.constants import DayOfWeek
from src.factories.base_factories import BaseFactory
from src.factories.base_factories import BasePolyFactory
from src.models import Theme
from src.tavern import Menu
from src.tavern.models import MenuItem


@register
class MenuItemFactory(BaseFactory):
    class Meta:
        model = MenuItem

    food = factory.Sequence(lambda n: f"Test Food {n}")
    day_of_the_week = factory.Iterator(DayOfWeek)
    menu = None


class MenuItemPolyFactory(BasePolyFactory[MenuItem]):
    __model__ = MenuItem
    __set_as_default_factory_for_type__ = True


@register
class MenuFactory(BaseFactory):
    class Meta:
        model = Menu

    server_id = sentinel.guild_id
    start_date = factory.Faker("date_object")
    items = factory.RelatedFactoryList(MenuItemFactory, factory_related_name="menu")


class MenuPolyFactory(BasePolyFactory[Menu]):
    __model__ = Menu
    __set_as_default_factory_for_type__ = True

    @post_generated
    @classmethod
    def start_date(cls) -> date:
        return cls.__faker__.date_object()


@register
class ThemeFactory(BaseFactory):
    class Meta:
        model = Theme

    name = factory.Sequence(lambda n: f"Test Theme {n}")


class ThemePolyFactory(BasePolyFactory[Theme]):
    __model__ = Theme
    __set_as_default_factory_for_type__ = True
