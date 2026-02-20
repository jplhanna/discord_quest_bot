from typing import Final

QUEST_COLUMN_NAME: Final = "Quests"
EXPERIENCE_COLUMN_NAME: Final = "XP"
BOX_VERTICAL_CHAR: Final = "="
BOX_SIDE_CHAR: Final = "||"
BLOCK_PRE_TEXT: Final = BOX_SIDE_CHAR + "  "
BLOCK_POST_TEXT: Final = "  " + BOX_SIDE_CHAR
CODE_BLOCK: Final = "```"
WRAPPER_TEXT_LEN: Final = len(BLOCK_POST_TEXT) + len(BLOCK_PRE_TEXT)
MINIMUM_SPACING: Final = 2
