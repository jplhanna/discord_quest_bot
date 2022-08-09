from src.helpers.message_helpers import format_quest_board
from src.models import Quest


class TestFormatQuestBoard:
    def test_base_case(self):
        # Act
        board = format_quest_board([])
        # Assert
        assert board == "No available quests"

    def test_single_case(self):
        # Arrange
        quest = Quest(name="Test Quest", experience=50)
        # Act
        board = format_quest_board([quest])
        # Assert
        assert (
            board == "```\n"
            "======================\n"
            "||  Quests      XP  ||\n"
            "||  Test Quest  50  ||\n"
            "======================\n"
            "```"
        )
