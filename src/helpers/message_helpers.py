from typing import List

from src.helpers.constants import BOX_WRAPPER_CHAR
from src.helpers.constants import CODE_BLOCK
from src.helpers.constants import EXPERIENCE_COLUMN_NAME
from src.helpers.constants import MINIMUM_SPACING
from src.helpers.constants import POST_TEXT
from src.helpers.constants import PRE_TEXT
from src.helpers.constants import QUEST_COLUMN_NAME
from src.helpers.constants import WRAPPER_TEXT_LEN
from src.models import Quest


def _create_single_quest_line(first_column: str, second_column: str, line_length: int) -> str:
    num_spaces_needed = line_length - WRAPPER_TEXT_LEN - len(first_column) - len(second_column)
    single_line = "".join([PRE_TEXT, first_column, " " * num_spaces_needed, second_column, POST_TEXT])
    return single_line


def format_quest_board(quests: List[Quest]) -> str:
    if not quests:
        return "No available quests"
    max_title_length = max([len(quest.name) for quest in quests] + [len(QUEST_COLUMN_NAME)])
    max_xp_length = max([len(str(quest.experience)) for quest in quests] + [len(EXPERIENCE_COLUMN_NAME)])
    line_length = max_title_length + max_xp_length + WRAPPER_TEXT_LEN + MINIMUM_SPACING
    board_top_and_bottom = BOX_WRAPPER_CHAR * line_length
    header = _create_single_quest_line(QUEST_COLUMN_NAME, EXPERIENCE_COLUMN_NAME, line_length)
    board_quest_text = [_create_single_quest_line(quest.name, str(quest.experience), line_length) for quest in quests]
    full_board = "\n".join(
        [CODE_BLOCK, board_top_and_bottom, header, *board_quest_text, board_top_and_bottom, CODE_BLOCK]
    )
    return full_board
