# Message Strings
from enum import IntEnum

GOOD_LUCK_ADVENTURER = "You have accepted {}! Good luck adventurer"
QUEST_ALREADY_ACCEPTED = "You have already accepted this request"
QUEST_DOES_NOT_EXIST = "This quest does not exist"


# Enums
class DayOfWeek(IntEnum):
    SUNDAY = 1
    MONDAY = 2
    TUESDAY = 3
    WEDNESDAY = 4
    THURSDAY = 5
    FRIDAY = 6
    SATURDAY = 7
