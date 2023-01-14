from typing import Any

from src.constants import QUEST_ALREADY_ACCEPTED
from src.constants import QUEST_DOES_NOT_EXIST
from src.models import Quest


class OutOfSessionContext(Exception):
    ...


class NoIDProvided(Exception):
    ...


class BaseQuestException(Exception):
    quest: Quest
    message: str

    def __init__(self, quest: Quest, *args: Any) -> None:
        super().__init__(self.message, *args)
        self.quest = quest


class QuestDNE(Exception):
    quest_name: str
    message = QUEST_DOES_NOT_EXIST

    def __init__(self, quest_name: str, *args: Any) -> None:
        super().__init__(self.message, *args)
        self.quest_name = quest_name


class QuestAlreadyAccepted(BaseQuestException):
    message = QUEST_ALREADY_ACCEPTED


class QuestNotAccepted(BaseQuestException):
    message = "You have not accepted this quest."


class MaxQuestCompletionReached(BaseQuestException):
    message = "You cannot complete this quest anymore times."
