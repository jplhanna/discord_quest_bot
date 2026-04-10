from typing import Final

QUEST_COLUMN_NAME: Final[str] = "Quests"
EXPERIENCE_COLUMN_NAME: Final[str] = "XP"
BOX_VERTICAL_CHAR: Final[str] = "="
BOX_SIDE_CHAR: Final[str] = "||"
BLOCK_PRE_TEXT: Final[str] = BOX_SIDE_CHAR + "  "
BLOCK_POST_TEXT: Final[str] = "  " + BOX_SIDE_CHAR
CODE_BLOCK: Final[str] = "```"
WRAPPER_TEXT_LEN: Final[int] = len(BLOCK_POST_TEXT) + len(BLOCK_PRE_TEXT)
MINIMUM_SPACING: Final[int] = 2
