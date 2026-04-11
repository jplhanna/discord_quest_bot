from typing import Any

import factory

from polyfactory import PostGenerated
from pytest_factoryboy import register

from src.factories.base_factories import BaseFactory
from src.factories.base_factories import BasePolyFactory
from src.factories.user_factories import UserFactory
from src.quests import ExperienceTransaction
from src.quests import Quest
from src.quests import UserQuest


@register
class QuestFactory(BaseFactory):
    id = factory.Sequence(lambda n: n + 1)

    class Meta:
        model = Quest

    name = "Test Quest"
    experience = 100


class QuestPolyFactory(BasePolyFactory[Quest]):
    __model__ = Quest
    __set_as_default_factory_for_type__ = True


@register
class UserQuestFactory(BaseFactory):
    class Meta:
        model = UserQuest

    date_completed = factory.Maybe("is_completed", yes_declaration=factory.Faker("date_between", start_date="-10d"))

    user = factory.SubFactory(UserFactory)
    quest = factory.SubFactory(QuestFactory)

    @factory.post_generation
    def append_to_quests(self, _create: bool, _extracted: Any, **_kwargs: Any) -> None:
        self.user.quests.append(self.quest)


class UserQuestPolyFactory(BasePolyFactory[UserQuest]):
    __model__ = UserQuest
    __set_as_default_factory_for_type__ = True


@register
class ExperienceTransactionFactory(BaseFactory):
    class Meta:
        model = ExperienceTransaction

    quest = factory.SubFactory(QuestFactory)
    experience = factory.SelfAttribute("quest.experience")
    user = factory.SubFactory(UserFactory)


class ExperienceTransactionPolyFactory(BasePolyFactory[ExperienceTransaction]):
    __model__ = ExperienceTransaction
    __set_as_default_factory_for_type__ = True

    experience = PostGenerated(lambda _name, values, *_args, **_kwargs: values["quest"].experience)
