import inspect
import sys

from .base_factories import BaseFactory
from .quest_factories import *  # noqa: F403
from .tavern_factories import *  # noqa: F403
from .user_factories import *  # noqa: F403

fact_classes = inspect.getmembers(sys.modules[__name__], lambda x: inspect.isclass(x) and issubclass(x, BaseFactory))
factory_classes = [cls for cls_name, cls in fact_classes if cls_name != "BaseFactory"]
