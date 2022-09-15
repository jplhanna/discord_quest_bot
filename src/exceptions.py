from typing import Any

from src.constants import QUEST_DOES_NOT_EXIST


class OutOfSessionContext(Exception):
    ...


class NoIDProvided(Exception):
    ...


class BaseQuestException(Exception):
    quest_name: str
    message: str

    def __init__(self, quest_name: str, *args: Any) -> None:
        super().__init__(self.message, *args)
        self.quest_name = quest_name


class QuestDNE(BaseQuestException):
    message = QUEST_DOES_NOT_EXIST


class QuestNotAccepted(BaseQuestException):
    message = "You have not accepted this quest"
