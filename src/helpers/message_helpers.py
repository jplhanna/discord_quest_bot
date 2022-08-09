from typing import List

from src.models import Quest

QUEST_BOARD_SPACING = 2
QUEST_BOARD_TEXT = "-  **{name}**  **{experience}**  -"
QUEST_COLUMN_NAME = "Quests"
EXPERIENCE_COLUMN_NAME = "XP"
BOX_WRAPPER_CHAR = "="


def _create_single_quest_line(first_column: str, second_column: str, max_line_length: int) -> str:
    num_spaces_needed = max_line_length - (3 * QUEST_BOARD_SPACING) - len(first_column) - len(second_column)
    single_line = "".join(
        [BOX_WRAPPER_CHAR, "  **", first_column, " " * num_spaces_needed, second_column, "**  ", BOX_WRAPPER_CHAR]
    )
    return single_line


def format_quest_board(quests: List[Quest]) -> str:
    if not quests:
        return "No available quests"
    max_title_length = max([len(quest.name) for quest in quests] + [len(QUEST_COLUMN_NAME)])
    max_xp_length = max([len(str(quest.experience)) for quest in quests] + [len(EXPERIENCE_COLUMN_NAME)])
    max_line_length = max_title_length + max_xp_length + (3 * QUEST_BOARD_SPACING) + 2
    board_top_and_bottom = BOX_WRAPPER_CHAR * max_line_length
    header = _create_single_quest_line(QUEST_COLUMN_NAME, EXPERIENCE_COLUMN_NAME, max_line_length)
    board_quest_text = [
        _create_single_quest_line(quest.name, str(quest.experience), max_line_length) for quest in quests
    ]
    full_board = "\n".join([board_top_and_bottom, header, *board_quest_text, board_top_and_bottom])
    return full_board
