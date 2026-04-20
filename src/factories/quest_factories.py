from polyfactory import PostGenerated

from src.factories.base_factories import BaseFactory
from src.quests import ExperienceTransaction
from src.quests import Quest
from src.quests import UserQuest


class QuestFactory(BaseFactory[Quest]):
    __model__ = Quest
    __set_as_default_factory_for_type__ = True


class UserQuestFactory(BaseFactory[UserQuest]):
    __model__ = UserQuest
    __set_as_default_factory_for_type__ = True


class ExperienceTransactionFactory(BaseFactory[ExperienceTransaction]):
    __model__ = ExperienceTransaction
    __set_as_default_factory_for_type__ = True

    experience = PostGenerated(lambda _name, values, *_args, **_kwargs: values["quest"].experience)
