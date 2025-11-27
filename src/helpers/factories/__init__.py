import inspect
import sys

from .base_factories import BaseFactory
from .quest_factories import *  # noqa: F403
from .tavern_factories import *  # noqa: F403
from .user_factories import *  # noqa: F403

_factory_classes = inspect.getmembers(
    sys.modules[__name__], lambda x: inspect.isclass(x) and issubclass(x, BaseFactory)
)
FACTORY_CLASSES = [cls for cls_name, cls in _factory_classes if not cls._meta.abstract]
