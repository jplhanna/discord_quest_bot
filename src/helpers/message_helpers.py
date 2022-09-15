from src.helpers.constants import BLOCK_POST_TEXT
from src.helpers.constants import BLOCK_PRE_TEXT
from src.helpers.constants import BOX_VERTICAL_CHAR
from src.helpers.constants import CODE_BLOCK
from src.helpers.constants import EXPERIENCE_COLUMN_NAME
from src.helpers.constants import MINIMUM_SPACING
from src.helpers.constants import QUEST_COLUMN_NAME
from src.helpers.constants import WRAPPER_TEXT_LEN
from src.models import Quest


def _create_single_quest_line(first_column: str, second_column: str, line_length: int) -> str:
    num_spaces_needed = line_length - WRAPPER_TEXT_LEN - len(first_column) - len(second_column)
    single_line = "".join([BLOCK_PRE_TEXT, first_column, " " * num_spaces_needed, second_column, BLOCK_POST_TEXT])
    return single_line


def format_quest_board(quests: list[Quest]) -> str:
    """
    This function formats a list of quests to look like a quest board
    The formatting is normalized so that all quest names and XP values start at the same char position
    Since Quests is len 6 and XP is len 2 the minimum line length is 18, and each column has minimum length 6 and 2.

    :param quests: List of quests to represent.
    :return: A code block of text which represents a list of quest names and how much XP that quest is worth.
    """
    if not quests:
        return "No available quests"
    max_title_length = max([len(quest.name) for quest in quests] + [len(QUEST_COLUMN_NAME)])
    max_xp_length = max([len(str(quest.experience)) for quest in quests] + [len(EXPERIENCE_COLUMN_NAME)])
    line_length = max_title_length + max_xp_length + WRAPPER_TEXT_LEN + MINIMUM_SPACING
    board_top_and_bottom = BOX_VERTICAL_CHAR * line_length
    header = _create_single_quest_line(QUEST_COLUMN_NAME, EXPERIENCE_COLUMN_NAME, line_length)
    board_quest_text = [_create_single_quest_line(quest.name, str(quest.experience), line_length) for quest in quests]
    full_board = "\n".join(
        [CODE_BLOCK, board_top_and_bottom, header, *board_quest_text, board_top_and_bottom, CODE_BLOCK]
    )
    return full_board
