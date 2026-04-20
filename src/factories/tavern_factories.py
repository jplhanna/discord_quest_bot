from datetime import date

from polyfactory.decorators import post_generated

from src.factories.base_factories import BaseFactory
from src.models import Theme
from src.tavern import Menu
from src.tavern.models import MenuItem


class MenuItemFactory(BaseFactory[MenuItem]):
    __model__ = MenuItem
    __set_as_default_factory_for_type__ = True


class MenuFactory(BaseFactory[Menu]):
    __model__ = Menu
    __set_as_default_factory_for_type__ = True

    @post_generated
    @classmethod
    def start_date(cls) -> date:
        return cls.__faker__.date_object()


class ThemeFactory(BaseFactory[Theme]):
    __model__ = Theme
    __set_as_default_factory_for_type__ = True
