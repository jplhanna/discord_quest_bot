from unittest.mock import sentinel

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
    server_id = sentinel.guild_id


class ThemeFactory(BaseFactory[Theme]):
    __model__ = Theme
    __set_as_default_factory_for_type__ = True
