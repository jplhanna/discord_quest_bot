from typing import Any

import factory

from pytest_factoryboy import register

from src.helpers.factories.base_factories import BaseFactory
from src.helpers.factories.user_factories import UserFactory
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


@register
class ExperienceTransactionFactory(BaseFactory):
    class Meta:
        model = ExperienceTransaction

    quest = factory.SubFactory(QuestFactory)
    experience = factory.SelfAttribute("quest.experience")
    user = factory.SubFactory(UserFactory)


@register
class UserWithQuestFactory(UserFactory):
    quest = factory.RelatedFactory(UserQuestFactory, factory_related_name="user")
    experience = factory.Maybe(
        "quest__is_completed",
        yes_declaration=factory.RelatedFactory(
            ExperienceTransactionFactory, factory_related_name="user", quest=factory.SelfAttribute("quest")
        ),
    )
