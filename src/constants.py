# Message Strings
from enum import Enum
from enum import IntEnum
from enum import auto
from typing import Final

GOOD_LUCK_ADVENTURER: Final = "You have accepted {}! Good luck adventurer"
QUEST_ALREADY_ACCEPTED: Final[str] = "You have already accepted this request"
QUEST_DOES_NOT_EXIST: Final = "This quest does not exist"
TEMP_CONST: Final[str] = "temp"


# Enums
class DayOfWeek(IntEnum):
    SUNDAY = 1
    MONDAY = 2
    TUESDAY = 3
    WEDNESDAY = 4
    THURSDAY = 5
    FRIDAY = 6
    SATURDAY = 7


class ChooseStyle(Enum):
    RANDOM = auto()
    FIRST = auto()
