from polyfactory import PostGenerated

from factories.base_factories import BaseFactory
from quests import ExperienceTransaction
from quests import Quest
from quests import UserQuest


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
