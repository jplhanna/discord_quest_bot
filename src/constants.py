# Message Strings
from enum import IntEnum

GOOD_LUCK_ADVENTURER = "You have accepted {}! Good luck adventurer"
QUEST_ALREADY_ACCEPTED = "You have already accepted this request"
QUEST_DOES_NOT_EXIST = "This quest does not exist"


# Enums
class DayOfWeek(IntEnum):
    sunday = 1
    monday = 2
    tuesday = 3
    wednesday = 4
    thursday = 5
    friday = 6
    saturday = 7
